#### **Status: In Development, not recommended.**

This is an **experimental** matchmaking system meant to be used in conjunction with the [get5](https://github.com/splewis/get5) CS:GO server plugin. It is built for small communities in CSGO to have matches against other players in community.

##**WARNING**: YOU SHOULD NOT USE THIS AT THIS STAGE. IT HAS BUGS. THE PROJECT IS STILL NOT FINISHED.


## Idea behind:
1. The community leader sign up as the first user and is assigned as `admin`. He can invite 3 more users to the platform (and can promote any user to admin or moderator)
2. Users join using invite-code and other important details.
3. Admins can add CSGO servers with `get5 by splewis` installed in 'servers' section.
4. Other users can queue for a match as solo or with a party.
5. After a match is found, map veto begins between the two teams.
6. After map(s) (BO3 or BO5 options also available) is(are) decided, server connect link is provided.
7. `get5` handles the match here onwards and reports the results to this server API
8. Players skill level is adjusted and match information along with demo file is available to the player.
9. Furthur plans to create a tournament and automate the process of conducting the tournament to be added (or another project).

Note: When using this MM system, the CS:GO game servers (that admins add) **must** have both the core get5 plugin and the get5_apistats plugin. They are [released](https://github.com/splewis/get5/releases) together. This means the server must also be running the [Steamworks](https://forums.alliedmods.net/showthread.php?t=229556) and [SMJansson](https://forums.alliedmods.net/showthread.php?t=184604) extensions.

## Requirements:
- python3.8
- MySQL (sqlite also work if DB not availabe)
- a linux web server capable of running Flask applications

