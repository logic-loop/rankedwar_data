# rankedwar_data
just a ranked war data set to play around with

## Scripts
* [pull_data.py](pull_data.py) - uses api key to pull sample of data, append to ```raw/data.json```
* [make_spreadsheets.py](make_spreadsheets.py) - takes raw data, does some transforms, adds a couple features, writes out
  * ```intermediate\member_participation.csv``` memberwise stats, including level and scores, date offset for x axis
  * ```intermediate\war_pair_data.csv``` one war per line
  * ```intermediate\war_reward_dataset.csv``` one line per faction per war
* [profile_data.py](profile_data.py) - uses ydata to generate generic dataset profiles (N ~= 700 wars when i ran the profiling)
* [explore_dataset.ipynb] - some graphs and things i found mildly interesting
* [text](do_regression.py)
* [text](explore_dataset.ipynb)

## Questions
* What's the algorithm for determining ranked war rewards?
* What's typical player participation look like? does it differ for winners / losers?
* Do players change their participation rates as they get stronger?
* What does a typical win / lose path look like for a given faction over time? (may need to pull more data) (thinking like random walk visualization - just cumulative total over time)