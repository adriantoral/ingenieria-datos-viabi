/**
 * @type {import('semantic-release').GlobalConfig}
 */

const releaseConfig = {
	branches: [
		'main',
		'develop'
	],
	plugins : [
		[
			'@semantic-release/commit-analyzer',
			{
				preset      : 'angular',
				releaseRules: [
					{ type: 'feat', release: 'minor' },
					{ type: 'fix', release: 'patch' },
					{ type: 'chore', release: false }
				],
				parserOpts  : {
					mergeCommitPattern : /^Merge pull request #(\d+) from (.*)$/,
					mergeCorrespondence: [ 'id' ]
				}
			}
		],
		'@semantic-release/release-notes-generator',
		[
			'@semantic-release/changelog',
			{
				changelogFile: 'CHANGELOG.md'
			}
		],
		'@semantic-release/git',
		'@semantic-release/github'
	]
};

export default releaseConfig;
