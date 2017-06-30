## Change Log

- [hifumi.py](https://github.com/hifumibot/hifumibot/blob/3a87be1970b4e3a3b5986c5773835a6e03954836/bot/hifumi.py) has been refactored.
- Bot now reports errors to an error log channel that can be set in configs.
- [DataManager](https://github.com/hifumibot/hifumibot/blob/d9f1c79272bde923e3981bb8f47aad7f37b2c256/data_controller/data_manager.py) class now preload data from the DB before bot start up. This addresses issue #8.
- ~~[Postgres](https://github.com/hifumibot/hifumibot/blob/d9f1c79272bde923e3981bb8f47aad7f37b2c256/data_controller/postgres.py) class now use the `execute_task` decorator to ensure only one task is being excuted at the same time.~~
- [Postgres](https://github.com/hifumibot/hifumibot/blob/fd57837aff13eae3b9f81f6959f7a4ca4bd11e10/data_controller/postgres.py) class now use a connection pool instead of a single connection to avoid locking issues.
- [SessionManager](https://github.com/hifumibot/hifumibot/blob/d9f1c79272bde923e3981bb8f47aad7f37b2c256/bot/session_manager.py) class now has methods to get json values from an HTTP request. This addresses issue #17.
- The bot now uses the root logger instead of the discord logger. This allows us to log at a lower level without clogging the logs with unneeded information.
- We have added empty command placeholders for the old Hifumi commands.