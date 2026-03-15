db = db.getSiblingDB('dhisppo_db');

db.createCollection('users');
db.users.createIndex({ "username": 1 }, { unique: true });
db.users.createIndex({ "email": 1 }, { unique: true });

db.createCollection('resolutions');
db.resolutions.createIndex({ "user_id": 1 });
db.resolutions.createIndex({ "created_at": 1 });

db.createCollection('events');
db.events.createIndex({ "organizers": 1 });
db.events.createIndex({ "locations": 1 });
db.events.createIndex({ "created_at": 1 });
db.events.createIndex({ "participants.user_id": 1 });

print('Database initialization completed successfully!');