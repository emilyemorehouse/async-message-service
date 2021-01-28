# Async Message Service

This repository holds companion source code for "Learning in Public — Building
a High Performance Async Response Queue using Python" that was presented for
[O'Reilly's Open Source Software Superstream Series: Python—Tips and Tricks,Machine Learning, and What’s New in 3.9 and Beyond](https://learning.oreilly.com/live-training/courses/open-source-software-superstream-series-pythontips-and-tricks-machine-learning-and-whats-new-in-39-and-beyond/0636920052151/#schedule).

The repository is tagged with steps to follow through the talk (and beyond):

- `step-0`: Base project code
- `step-0b` (branched on `this-is-not-the-asyncio-youre-looking-for`): Example anti-patterns for async code that is not actually concurrent
- `step-1a`: Adding basic `ack`s
- `step-1b`: Storing command responses
- `step-1c`: Fancy awaitable `ack`s!
- `step-2.`:Retries
- `step-3a`: Exception handling
- `step-3b`: More exception handling

## ⬆️ Getting Started

### 📦 Dependencies

The only dependency required, outside of Python 3.8+, is [attrs](https://www.attrs.org/en/stable/).

I recommend setting up a virtual environment with your tool of choice to install from the
`requirements.txt`.

### ▶️ Running the App

Once you have `attrs` installed, run: `python command-registry.py`. You can stop it with `ctrl+c`.

## 🗣 Shout Outs

A huge "thank you" to [Lynn Root](https://twitter.com/roguelynn), whose blog series,
["asyncio: We Dit It Wrong"](https://www.roguelynn.com/words/asyncio-we-did-it-wrong/) got me
started on this project!

## 👟 Suggested Next Steps

Here's a list of features that I think would be interesting to add and that I've used in real-world
projects:

- multiple responses, e.g. for subscriptions
- custom command timeouts
- command tracking: time at which the command was received, time at which first response was
  received, etc.
- command priorities
