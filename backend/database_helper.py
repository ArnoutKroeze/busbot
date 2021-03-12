import sqlite3
import os

# Get some things from a database because i dont want to bother reddit for each request? i guess?
# At least I have klokmemes on my pc now


class DatabaseHelper():

    def __init__(self, dbname="alle_fotos.sqlite", data_location="/home/arnout/media/fotos/reddit"):
        self.db = sqlite3.connect(dbname)
        self.cursor = self.db.cursor()
        self.PATH = data_location


    def handle_return(self, *args):

        try:
            title, file, subreddit = list(*args)[0]
            file = os.path.join(self.PATH, subreddit, file)
            return file, title
        except ValueError:
            # if there are no such photos
            return False, False
        except Exception as e:
            print(e)
            return False, False


    
    def random_by_subreddit(self, subreddit="klokmemes"):
        # Returns a random image from this subreddit

        self.cursor.execute('''SELECT title, filename, subreddit FROM alle_fotos WHERE subreddit=? 
                            ORDER BY RANDOM() LIMIT 1''',
                (subreddit,))     

        return self.handle_return(self.cursor.fetchall()[0])

    def random_by_title(self, title: str):
        # Returns a random image whose title contains this substring. This is case-insensitive.
        # ('pils' LIKE %'GROLSCH PILSENER'%) is true

        self.cursor.execute('''
            SELECT title, filename, subreddit FROM alle_fotos WHERE title LIKE ? ORDER BY RANDOM() LIMIT 1''',
            ('%' + title + '%',))
        
        return self.handle_return(self.cursor.fetchall()[0])

    def random_by_title_and_sub(self, title: str, subreddit='klokmemes'):
        self.cursor.execute('''
            SELECT title, filename, subreddit FROM alle_fotos WHERE title LIKE ? AND subreddit=? ORDER BY RANDOM() LIMIT 1''',
            ('%' + title + '%', subreddit))
        
        return self.handle_return(self.cursor.fetchall())