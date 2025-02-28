rss-kindle
This is a simple python script that will run on a schedule to aggregate a couple of my favorite free rss sources, format them, and then email them as a .txt file to my kindle via use of the "Send to kindle" service Amazon offers.

How to get started (On macOS, sorry windows freaks):
Fork this repo and then clone that to your machine
git clone https://github.com/{User-name}/rss-kindle cd rss-kindle git remote add upstream git@github.com:jbrauck-unchained/rss-kindle

Verify that your remotes are setup should show your origin and the upstream git remote -v

Create a virtual environment
python -m venv venv

source venv/bin/activate

Install libraries
pip install feedparser pip install requests pipinstall python-dotenv

Copy .env.example to .env and edit environment variables
cp .env.example .env

To make changes
Create a branch from main by using git checkout -b 'branch-name-here’

As you make your changes, add files, do commits.

When ready, push commits to your branch’s remote git push origin

This will push the changes to your local fork, and then when looking at the original repo you should be prompted to create a pull request for your changes. Set the title, description, and create.

I will review the changes and merge if they add value to the repo.
