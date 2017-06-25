# TODO
## 1. Bot manager/launcher
- [ ] Rework all functions

## 2. Bot base and command handler
- mostly finished, contiune to add onto it if needed
- [ ] Check wether there are news about discord.py library rewrite
- [ ] If needed, restructure the functions if that happens

## 3. Current hifumi commands transfering
#### Fun
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

#### Interactions
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
#### Utilities/Search
* osu/setosu moved to its own category
* shorten removed cuz I said so
* anime/manga moved to its own category
* serverinfo/userinfo/avatar/birthday/nicknames moved to its own category
* fact commands made into command group
* dog facts removed due to no good api  
* yesno removed because shit api

```
advice              ✔
fact                ✔
fact cat            ✔
fact number *new    ✔
imdb                ✔
recipe              ✔
remindme            ✕
strawpoll           ✕
time                ✕
twitch              ✕
urban               ✕
weather             ✕
```

#### Roles :white_check_mark:
```
rolelist            ✔
roleme              ✔
unroleme            ✔
selfrole add        ✔
selfrole remove	    ✔
```
#### Moderation :white_check_mark:
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

#### Music
* Using temporary module for now, rewrite later

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
#### Tags
```
tag create          ✕
tag delete          ✕
tag edit            ✕
tag owner           ✕
```
#### NSFW :white_check_mark:
* rule34 is removed due to dead api

```
e621                ✔
konachan            ✔
yandere             ✔
danbooru *new       ○
gelbooru *new       ○
greenteaneko        ✔
```
#### Bot info
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
#### Owner only
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

#### Currency
```
daily               ✔
balance             ✔
transfer            ✔
market              ✕
slots               ✔
trivia              ✔
```

#### Osu
```
osu                 ✕
setosu              ✕
```

#### Weeb
```
anime               ✕
manga               ✕
```

#### User/Server Info
```
avatar              ✕
birthday            ✕
nicknames           ✕
serverinfo          ✕
userinfo            ✕
```

## 4. New features
- [ ] A bot stats updater (post discordlist.org, carbonitex.net and discord.bots.pw stats every hour)
- [ ] Actual polls via Discord instead of Strawpoll
- [ ] Add ban, softban and kick notifications for modlog! If possible, also include server general actions, like audit log
- [ ] Addition of Chuck Norris jokes (name customizable)
- [ ] Announce when there's the birthday for someone
- [ ] As people is requesting it too much, instead of people's permissions, replace that with commands permissions like Rem's system.
- [ ] Autorole function (assign a role to new members)
- [ ] Battle command to defeat from other users
- [ ] Calculator for math, if possible scientific
- [ ] Cleaning filters (clean bot messages, all bots messages, specific user messages)
- [ ] Cleverbot return
- [x] Danbooru, Gelbooru and Safebooru addition
- [ ] Fix the bug for shard ID argument instead of settings
- [x] Format errors when bot DMs
- [ ] Google searching, as well as images and videos
- [ ] Hackban (ban users outside the server via user ID) and individual unban as well
- [ ] Invite blocker and mention spam protection
- [ ] Imgur command
- [ ] Level up system (a.k.a. XP system), I'll explain this later if doing that feature someday
- [ ] Love Live! school idols information because why not (this <a href="https://github.com/SchoolIdolTomodachi/SchoolIdolAPI">API</a>)
- [ ] Make a waifu command (search random Google pictures for the bot character, this can be specified in settings.py; in the public version the command should be "~hifumi")
- [ ] Make another meme command but with user avatar (For example spoo.py "Fun" category commands or t!beautiful from Tatsumaki)
- [ ] Make possible a triggered command with the picture of a user (with filters, like blargbot)
- [ ] Merge cute(x) commands to a new animal command
- [ ] Message to general channel of bot introduction when bot joins to a new guild
- [x] Modlog
- [ ] osu! pp calculating for beatmaps
- [ ] Profile for currency
- [ ] Raffle (pretty simple, just send a message with random user of the server, useful for raffles or giveaways)
- [x] Recipe finder
- [ ] Softban function (also with modlog, ban someone and then unban him)
- [ ] Stats for other games besides osu! like Overwatch, Steam profile, World of Warships, CSGO, LOL, etc.
- [ ] Stream Listen.moe via command
- [ ] Stream notification available too for Twitch, Hitbox and Beam
- [ ] Tag commands back but with a "HifumiLang" system, I'll expalin this too when doing the future someday
- [ ] Text converting than just leetspeak (leetspeak, zalgo, katakana, etc.)
- [ ] Toggle DM sending for Hifumi
- [ ] Translation command return
- [ ] Voteban! (yes, really; ask the vote of people to ban a person. Admin command to avoid abuse.)
- [ ] Welcome and farewell system, able for DM or channel
- [ ] "Who's that Pokemon?" trivia
- [ ] Wikipedia searching
- [ ] Word filter (mod tool, compatible with words and regex as well)

**NOTE:** Those are the best ideas we picked. Until we're done with them, we're not accepting feature requests anymore.

## 5. Translation support
   - Done! Locals are actually WIP

## 6. Documentation
   - coming soon!

## 7. Database transfer and final touches
   - coming soon!

## 8. Release
   - coming soon!
