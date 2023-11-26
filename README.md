# g_Bloxy's tower defense game

A tower defense game project.  
You can test it with different maps, golds or lifes quantity, changing the game variables in the level.py file.  
To test featurs, the dev-mode is set to 1 by default ( in the level.py file ). To play normally, set it to 0.

## Gameplay

There are 4 towers : basic tower, explosive bullets tower, rapid fire tower, and a barrack tower.
They can upgrade 2 times before choosing a path update.  
Building and upgrading towers cost gold, winned by killing enemies.  
Mobs spawns at all the spawns faster and faster.
If an ememy arrives at the end, you lose a life. The game end when you lose all your lifes.

## Controls ( temporary )

* Press ECHAP to quit.
* To build a tower, hover a slot and press 1, 2, 3, or 4, corresponding at the type of tower you want to build.
* To upgrade a tower before the path update, just left click the tower.
* To choose a tower path update, hover it and press 1, or 2.
* With the dev-mode :
  * press RIGHT to spawn a mob.
  * press UP / DOWN to increase / decrease the enemies spawn rate.

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
