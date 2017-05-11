# awwBot

## What Do?
The idea for this project is to provide a bot that will periodically post a cute picture from Reddit to a Slack channel and will also provide a interactive Slack Bot that will allow users to run queries such as: "Hey @awwbot send @user a cute picture of a puppy" and various other un-thought-of features. I plan to implement the Filestack Image Tagging API to tag images with things like: dog, cat, person, etc. as well as verify that all pictures I am scraping are SFW.

## How to Get Started
It's a bit of a process and I'm considering changing the tools I am using, but basically you just need to install the requirements.txt (I'm using python 3.4 - no reason in particular, just what I have on my machine), create a awwbot.db file in the project directory, signup for a free API key with Filestack https://dev.filestack.com/register/, and if you want to use the post_message_to_slack method, you must create a Slack team and create an app and a couple more convoluted steps...
Once this project is more complete than it is now, I wish flesh out this README to be more helpful :)

## Suggestions
I think Github issues is convenient for this. Just keep in mind that the repo is public, so you might get some dialog going with people other than myself.

## Contributing
PRs should be suitable if you see anything in particular that could be done better. I will most likely try to understand, by asking you, what the change does and why it might be necessary before implementing it though.
