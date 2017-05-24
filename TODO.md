# TODO
## 1. Bot manager/launcher
- Done
## 2. Bot base and command handler
- mostly finished, contiune to add onto it if needed
## 3. Current hifumi commands transfering
1. Fun
```
8ball               ✕
accordingtodevin    ✕
choose              ✕
coinflip            ✕ 
cutecat             ✕
cutedog             ✕
dice                ✕
edgy                ✕
funfact             ✕
garfield            ✕
gif                 ✕
hifumi              ✕
@Hifumi             ✕
lewd                ✕
love                ✕
meme                ✕
meme list           ✕      
rate                ✕
reverse             ✕ 
rip                 ✕
roll                ✕
rps                 ✕
say                 ✕
smug                ✕
triggered           ✕  
xkcd                ✕
yomomma             ✕
```
2. Interactions
```
cry                 ✕
cuddle              ✕
hug                 ✕
kiss                ✕
lick                ✕
eat                 ✕
pat                 ✕
pout                ✕
slap                ✕
stare               ✕
tickle              ✕
```
3. Utilities/Search
* osu/setosu moved to its own category
* shorten removed cuz I said so
* anime/manga moved to its own category
* serverinfo/userinfo/avatar/birthday/nicknames moved to its own category
* fact commands made into command group
* dog facts removed due to no good api
```
advice              ✔
fact                ✔
fact cat            ✔
fact number *new    ✔
imdb                ✔
recipe              ✕
remindme            ✕
strawpoll           ✕
time                ✕
twitch              ✕
urban               ✕
weather             ✕
yesno               ✕
```
4. Roles :white_check_mark:
```
rolelist            ✔
roleme              ✔
unroleme            ✔
selfrole add        ✔
selfrole remove	    ✔
```
5. Moderation :white_check_mark:
* setlevel removed in favour of role based permissions
* Mod log function is finished
```
ban                 ✔
kick                ✔
clean               ✔
mute                ✔
unmute              ✔
warn                ✔
pardon *new         ○
modlog *new         ○
modlog add *new     ○
modlog remove *new  ○
```
6. Music
```
join                ✕
request             ✕
song pause          ✕
song play           ✕
repeat              ✕
volume              ✕
np                  ✕
queue               ✕
queue clean         ✕
queue remove        ✕
shuffle             ✕
skip                ✕
forceskip           ✕
leave               ✕
```
7. Tags
```
tag create          ✕
tag delete          ✕
tag edit            ✕
tag owner           ✕
```
8. NSFW :white_check_mark:

* rule34 is removed due to dead api
```
e621                ✔
konachan            ✔
yandere             ✔
danbooru *new       ○
gelbooru *new       ○
greenteaneko        ✔
```
9. Bot info
```
info                ✔
support             ✔
donate              ✔
git                 ✔
help                ✕
ping                ✔
invite              ✔
language *new       ○
language list *new  ○
language set *new   ○
language reset *new ○
prefix              ✔
prefix set          ✔
prefix reset *new   ○
```
10. Owner only
```
bash                ✔
setavatar           ✔
eval                ✔
shard               ✕
shardinfo           ✕
editsettings        ✕
reload              ✕
restart             ✕
shutdown            ✕
blacklist           ✕
```

11. Currency
```
daily               ✔
balance             ✔
transfer            ✔
market              ✕
slots               ✔
trivia              ✔
```

12. Osu
```
osu                 ✕
setosu              ✕
```

13. Weeb
```
anime               ✕
manga               ✕
```

14. User/Server Info
```
avatar              ✕
birthday            ✕
nicknames           ✕
serverinfo          ✕
userinfo            ✕
```

## 4. New features
- [ ] A command to switch bot status (setstatus)
- [ ] AFK function (if a user that has AFK activated is mentioned, make Hifumi send a message with the reason if specified)
- [ ] Actual polls via Discord instead of Strawpoll
- [ ] Add ban and kick notifications for modlog !
- [ ] Addition of Chuck Norris jokes (name customizable) 
- [ ] Announce when there's the birthday for someone 
- [ ] Automatic hentai posting if set
- [ ] Autorole function (assign a role to new members)
- [ ] Battle command to defeat from other users 
- [ ] Calculator for math, if possible scientific
- [ ] Cleaning filters (clean bot messages, all bots messages, specific user messages)
- [ ] Cleverbot return
- [x] Danbooru, Gelbooru and Safebooru addition
- [ ] Display a list for 10 latest results if music is requested via search query, user can choose by typing the option number and then bot queues for play (Refer to Rem's !w.qa)
- [ ] Feedback (with cooldown to avoid abuse)
- [ ] Fix the bug for shard ID argument instead of settings 
- [ ] Format errors when bot DMs
- [ ] Google searching, as well as images
- [ ] Hackban (ban users outside the server via user ID) and individual unban as well
- [ ] Invite blocker and mention spam protection
- [ ] Lookup a Pokemon with number
- [ ] Make a waifu command (search random Google pictures for the bot character, this can be specified in settings.py; in the public version the command should be "~hifumi")
- [ ] Make another meme command but with user avatar (For example spoo.py "Fun" category commands or t!beautiful from Tatsumaki)
- [ ] Make an easy installer for Windows (graphic mode, planned)
- [ ] Make possible a triggered command with the picture of a user (with filters, like blargbot)
- [ ] Merge cute(x) commands to a new animal command
- [ ] Message to general channel of bot introduction when bot joins to a new guild, DM to a mod if bot is kicked (promote feedback) 
- [x] Modlog
- [ ] Profile for currency 
- [ ] Raffle (pretty simple, just send a message with random user of the server, useful for raffles or giveaways)
- [ ] Recipe finder
- [ ] RSS subscriptions and announcements
- [ ] Softban function (also with modlog, ban someone and then unban him)
- [ ] Stats for other games like Overwatch, Steam profile, World of Warships, CSGO, LOL, etc.
- [ ] Stream Listen.moe via command
- [ ] Stream notification available too for Hitbox and Beam
- [ ] Text converting than just leetspeak (leetspeak, zalgo, katakana, etc.)
- [ ] Toggle DM sending for Hifumi
- [ ] Translation command return
- [ ] Truth or dare
- [ ] Twitch stream notification 
- [ ] Voteban! (yes, really; ask the vote of people to ban a person. Admin command to avoid abuse.)
- [ ] Welcome and farewell system
- [ ] Wikipedia searching
- [ ] Word filter (compatible with words and regex as well)
- [ ] osu! pp calculating for beatmaps
- [ ] osu! beatmap status announce (for example: http://puu.sh/vXBKc.jpg)
- [ ] Modding queue activity for osu! (for example: http://puu.sh/vXDhg.jpg)

**NOTE:** Those are the best ideas we picked. Until we're done with them, we're not accepting feature requests anymore.
   
## 5. Translation support
   - Done! Locals are actually WIP
## 6. Documentation
   - coming soon!
## 7. Database transfer and final touches
   - coming soon!
## 8. Release
   - coming soon!
