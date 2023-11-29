# g_Bloxy's tower defense game

A tower defense game project.  
You can test it with different maps, golds or lifes quantity, changing the game variables in the level.py file.  
To test featurs, set the dev-mode to 1 ( in the level.py file ). To play normally, set it to 0 ( by default ).

## Gameplay

There are 4 towers : basic tower, explosive bullets tower, rapid fire tower, and a barrack tower.
They can upgrade 2 times before choosing a path update.  
Building and upgrading towers cost gold, winned by killing enemies.  
Mobs spawns at all the spawns faster and faster.
If an ememy arrives at the end, you lose a life. The game end when you lose all your lifes.

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
