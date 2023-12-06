# g_Bloxy's tower defense game

A tower defense game project.  
You can test it with different maps, golds or lives quantity, changing the game's variables in the level.py file.  
To test features, set the dev-mode to 1 ( in the level.py file ). To play normally, set it to 0 ( by default ).

## Gameplay

There are 4 towers : basic tower, explosive bullets tower, rapid fire tower, and barrack tower.
They each upgrade twice before branching out into two different path upgrade.
Building and upgrading towers costs gold, earned by killing enemies.
Mobs spawns at all the spawn points faster and faster.
If an ememy arrives at the end, you lose a life. The game ends when you lose all your lives.

## Controls

* Press ECHAP to quit.
* To select something in the tower ui, just click on the option you want.
* With the dev-mode :
  * press 1 to spawn a mob.
  * click a mob to kill it.
  * press 2 / 3 to increase / decrease the enemies spawn rate.

## Launch the game

Just execute the tower_defense.py file inside the game folder.

## Requirements

* Make sure you have [python](https://www.python.org) installed.  
* Use the package manager [pip](https://pip.pypa.io/en/stable/) to install [pygame](https://www.pygame.org/news).  
```bash
pip install pygame
```

## Contributing
 
If you encounter any issues, have suggestions, or need support, please don't hesitate to reach out by creating an issue in the repository.  
All feedbacks are welcome.
