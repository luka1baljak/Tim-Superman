from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Izlet

class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_befriend(self):
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.befriended.all(), [])
        self.assertEqual(u1.friends.all(), [])

        u1.befriend(u2)
        db.session.commit()
        self.assertTrue(u1.is_friends(u2))
        self.assertEqual(u1.befriended.count(), 1)
        self.assertEqual(u1.befriended.first().username, 'susan')
        self.assertEqual(u2.friends.count(), 1)
        self.assertEqual(u2.friends.first().username, 'john')

        u1.unfriend(u2)
        db.session.commit()
        self.assertFalse(u1.is_friends(u2))
        self.assertEqual(u1.befriended.count(), 0)
        self.assertEqual(u2.friends.count(), 0)

    def test_list_of_izlets(self):
        # create four users
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        u3 = User(username='mary', email='mary@example.com')
        u4 = User(username='david', email='david@example.com')
        db.session.add_all([u1, u2, u3, u4])

        # create four posts
        now=datetime.utcnow()
        izlet1= Izlet(naziv="Izlet u Belgiju",creator=u1,timestamp=now+timedelta(seconds=1))
        izlet2= Izlet(naziv="Izlet u Norvesku",creator=u2,timestamp=now+timedelta(seconds=4))
        izlet3= Izlet(naziv="Izlet u Francusku",creator=u3,timestamp=now+timedelta(seconds=3))
        izlet4= Izlet(naziv="Izlet u Svedsku",creator=u4,timestamp=now+timedelta(seconds=2))
        db.session.add_all([izlet1,izlet2,izlet3,izlet4])
        db.session.commit()


        u1.befriend(u2)
        u1.befriend(u4)
        u2.befriend(u3)
        u3.befriend(u4)
        db.session.commit()

        # check the followed posts of each user
        f1 = u1.izleti_prijatelja().all()
        f2 = u2.izleti_prijatelja().all()
        f3 = u3.izleti_prijatelja().all()
        f4 = u4.izleti_prijatelja().all()
        self.assertEqual(f1, [izlet2, izlet4, izlet1])
        self.assertEqual(f2, [izlet2, izlet3,izlet1])
        self.assertEqual(f3, [izlet2,izlet3, izlet4])
        self.assertEqual(f4, [izlet3,izlet4,izlet1,])

if __name__ == '__main__':
    unittest.main(verbosity=2)