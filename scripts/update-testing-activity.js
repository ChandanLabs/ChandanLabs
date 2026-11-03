'use strict';

const fs = require('node:fs');

const username = (process.env.GITHUB_USERNAME || process.env.GITHUB_REPOSITORY_OWNER || '').trim();
if (!username) {
  console.error('GITHUB_USERNAME or GITHUB_REPOSITORY_OWNER must be set.');
  process.exit(1);
}

const headers = {
  Accept: 'application/vnd.github+json',
  'X-GitHub-Api-Version': '2022-11-28',
  'User-Agent': 'ChandanLabs-testing-activity-profile'
};

async function getJson(url) {
  const response = await fetch(url, { headers });
  if (!response.ok) {
    const body = await response.text();
    throw new Error('GitHub API ' + response.status + ' for ' + url + ': ' + body.slice(0, 250));
  }
  return response.json();
}

const messagePattern = /\b(test(?:s|ing)?|qa|quality assurance|automation|automated|selenium|playwright|cypress|rest assured|restassured|testng|junit|cucumber|postman|regression|e2e|end[- ]to[- ]end|integration tests?|smoke tests?|assertions?)\b/i;
const pathPattern = /(^|\/)(test|tests|__tests__|e2e|integration|features|step[-_]definitions)(\/|$)|\.(spec|test)\.[^.]+$|(^|\/)(playwright|cypress|jest|vitest|pytest)\.config\.[^.]+$|(^|\/)(testng|pytest)\.ini$|(^|\/)conftest\.py$/i;

function cleanMessage(value) {
  return String(value || '').split(/\r?\n/)[0].trim().slice(0, 120).replace(/[&<>[\]]/g, ' ');
}

async function main() {
  const eventsUrl = 'https://api.github.com/users/' + encodeURIComponent(username) + '/events/public?per_page=100';
  const events = await getJson(eventsUrl);
  const pushes = events.filter((event) =>
    event.type === 'PushEvent' &&
    event.actor &&
    String(event.actor.login || '').toLowerCase() === username.toLowerCase() &&
    event.repo &&
    event.repo.name &&
    event.payload &&
    Array.isArray(event.payload.commits)
  );

  const candidates = [];
  const seen = new Set();
  for (const event of pushes) {
    for (const pushedCommit of (event.payload.commits || []).slice().reverse()) {
      const sha = String(pushedCommit.sha || '');
      if (!/^[a-f0-9]{40}$/i.test(sha) || seen.has(sha)) continue;
      seen.add(sha);
      candidates.push({
        sha,
        repo: event.repo.name,
        pushedMessage: pushedCommit.message || '',
        eventDate: event.created_at
      });
    }
  }

  // Keep API usage bounded. The workflow polls every six hours.
  const scan = candidates.slice(0, 35);
  const matches = [];

  for (const candidate of scan) {
    const encodedRepo = candidate.repo.split('/').map(encodeURIComponent).join('/');
    let commit;
    try {
      commit = await getJson(
        'https://api.github.com/repos/' + encodedRepo + '/commits/' + encodeURIComponent(candidate.sha)
      );
    } catch (error) {
      console.warn('Skipping commit ' + candidate.sha.slice(0, 7) + ': ' + error.message);
      continue;
    }

    // Ignore commits explicitly attributed to another GitHub account.
    const authorLogin = commit.author && commit.author.login
      ? String(commit.author.login).toLowerCase()
      : '';
    if (authorLogin && authorLogin !== username.toLowerCase()) continue;

    const message = cleanMessage((commit.commit && commit.commit.message) || candidate.pushedMessage);
    const files = Array.isArray(commit.files) ? commit.files : [];
    const matchingPaths = files
      .map((file) => String(file.filename || ''))
      .filter((path) => pathPattern.test(path));

    if (!messagePattern.test(message) && matchingPaths.length === 0) continue;

    const commitDate =
      (commit.commit && commit.commit.author && commit.commit.author.date) ||
      candidate.eventDate ||
      new Date().toISOString();

    matches.push({
      sha: candidate.sha,
      repo: candidate.repo,
      message: message || 'Testing-related changes',
      date: commitDate.slice(0, 10),
      url: commit.html_url || ('https://github.com/' + candidate.repo + '/commit/' + candidate.sha)
    });
  }

  matches.sort((a, b) => b.date.localeCompare(a.date));
  const visible = matches.slice(0, 6);

  const readmePath = 'README.md';
  let readme = fs.readFileSync(readmePath, 'utf8');
  const start = '<!-- TESTING-ACTIVITY:START -->';
  const end = '<!-- TESTING-ACTIVITY:END -->';
  const startIndex = readme.indexOf(start);
  const endIndex = readme.indexOf(end);
  if (startIndex < 0 || endIndex < 0 || endIndex < startIndex) {
    throw new Error('README testing activity markers are missing; refusing to rewrite the file.');
  }

  let body;
  if (visible.length === 0) {
    body = '<p><em>No recent public testing-focused commits detected in the latest scan. This section updates when testing-related commits are pushed to public repositories.</em></p>';
  } else {
    body = visible.map((entry) =>
      '- [' + entry.repo + '](' + entry.url + ') - ' +
      entry.message +
      ' · ' + entry.date + ' · ' + entry.sha.slice(0, 7)
    ).join('\n');
    body += '\n\n<sub>Detected from public commit messages and changed test-file paths. Detection is best-effort.</sub>';
  }

  const updated = readme.slice(0, startIndex + start.length) +
    '\n' + body + '\n' +
    readme.slice(endIndex);

  if (updated !== readme) {
    fs.writeFileSync(readmePath, updated, 'utf8');
    console.log('Updated README with ' + visible.length + ' testing-related public commit(s).');
  } else {
    console.log('Testing activity is unchanged (' + visible.length + ' matching public commit(s)).');
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
