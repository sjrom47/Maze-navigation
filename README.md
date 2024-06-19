# Maze Navigation Project 🧩🚀

This repository contains a project for generating mazes and developing agents to help users navigate them safely.

<!-- TABLE OF CONTENTS -->
- [Maze Navigation Project 🧩🚀](#maze-navigation-project-)
  - [About the project ℹ️](#about-the-project-ℹ️)
  - [Libraries and dependencies 📚](#libraries-and-dependencies-)
  - [Maze Generation](#maze-generation)
    - [Logical Maze](#logical-maze)
    - [Bayesian Maze](#bayesian-maze)
  - [Agent Development 🧠](#agent-development-)
    - [Logic-based agent](#logic-based-agent)
    - [Bayesian agent](#bayesian-agent)
  - [Search Algorithms 🔍](#search-algorithms-)
  - [How to use ⏩](#how-to-use-)
  - [Developers 🔧](#developers-)

## About the project ℹ️

This project involves creating a series of mazes with specific requirements and developing agents capable of helping users navigate through the mazes without falling into any traps. 
The player must find colonel Kurtz without stepping on traps and exit the maze

The project is divided into three main parts:
1. The mazes themselves, including their creation and characteristics.
2. The agents that help users reason about the positions of various maze elements.
3. Search algorithms that allow for automatic code execution.

## Libraries and dependencies 📚

> It is recommended to use Python version 3.10 to avoid possible incompatibilities with dependencies and libraries.

To install the required dependencies, run the following command:

```bash
pip install -r requirements.txt
```

## Maze Generation

The project includes two types of mazes: logical mazes and Bayesian mazes. There are slight differences between the mazes to better suit the agent, whether it be the logical or the bayesian agent
### Logical Maze

The logical maze includes the following elements:

    Player (CW)
    Monster (M)
    Three precipices (P)
    Exit (S)
    Colonel Kurtz (CK)

### Bayesian Maze

The Bayesian maze is used for probabilistic reasoning and includes the following elements:

    Player (CW)
    Monster (M)
    Three precipices (P)
    Exit (S)

## Agent Development 🧠

The agents in this project help users navigate the mazes by reasoning about the positions of various maze elements.

There are two types of agent: a logic-based agent and a bayesian agent

### Logic-based agent
This agent relies on the characteristics of the maze and the stimuli it receives to create a knowledge base from which it can infer the exact position of traps and other elements of the maze. It will help the player by revealing the contents of a square when it knows its content.

### Bayesian agent
This agent uses bayesian inference to calculate the probability of each element of the maze being in every square. This way, it can suggest a move by calculating which of the unknown squares the user is less likely to lose in. 


## Search Algorithms 🔍

The project includes search algorithms to automate the maze-solving process, which can be used for both mazes.

For the logical agent the search algorithm used is BFS, as we cannot perform informed search. However, we will avoid any square were the player could lose unless these are the only squares left. 

For the bayesian agent the search algorithm follows the recommendations of the bayesian agent.

However, there is another challenge. The player cannot simply teleport to the next square, they must navigate through the known parts of the maz to get to it. This is where A* comes in, finding the optimal path from one square to the next through just the known squares

## How to use ⏩

To run this project, run the `kurtz.py` file or use the following command:

```bash
python kurtz.py 
```

## Developers 🔧

Thank you for checking out this project. If you have any suggestions or questions, feel free to reach out.

   * [Sergio Jimenez](https://github.com/sjrom47)