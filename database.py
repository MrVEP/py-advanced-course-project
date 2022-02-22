import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from credentials import host, port, name, user, password
from VKapi.user_data import VKUser


class DBSetup:
    def __init__(self):
        self.host = host
        self.port = port
        self.name = name
        self.user = user
        self.password = password

    def create_db(self):
        return (
            f'postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}'
        )


db_setup = DBSetup()
engine = sq.create_engine(db_setup.create_db())
DB_Session = sessionmaker(bind=engine)

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String)
    last_name = sq.Column(sq.String)
    age = sq.Column(sq.Integer)
    sex = sq.Column(sq.Integer)
    city = sq.Column(sq.String)
    city_id = sq.Column(sq.Integer)
    age_from = sq.Column(sq.Integer)
    age_to = sq.Column(sq.Integer)
    results = relationship('Results', backref='users')


class Results(Base):
    __tablename__ = 'results'

    id = sq.Column(sq.Integer, primary_key=True)
    searcher_id = sq.Column(sq.Integer, sq.ForeignKey('users.id'))
    result_id = sq.Column(sq.Integer)


def get_all_users_id():
    db_session = DB_Session()
    users = db_session.query(Users.id).all()
    users_ids = [i[0] for i in users]
    db_session.close()
    return users_ids


def get_user_info(user_id: int):
    db_session = DB_Session()
    info = db_session.query(Users).filter(Users.id == user_id).all()[0]
    existing_user = VKUser(user_id)
    existing_user.first_name = info.first_name
    existing_user.last_name = info.last_name
    existing_user.age = info.age
    existing_user.sex = info.sex
    existing_user.city = info.city
    existing_user.city_id = info.city_id
    existing_user.age_range[0] = info.age_from
    existing_user.age_range[1] = info.age_to
    db_session.close()
    return existing_user


def add_user(new_user: VKUser):
    db_session = DB_Session()
    new_user_data = Users(id=new_user.id,
                          first_name=new_user.first_name,
                          last_name=new_user.last_name,
                          age=new_user.age,
                          sex=new_user.sex,
                          city=new_user.city,
                          city_id=new_user.city_id,
                          age_from=new_user.age_range[0],
                          age_to=new_user.age_range[1])
    db_session.add(new_user_data)
    db_session.commit()
    db_session.close()


def add_result(user_id: int, result_id: int):
    db_session = DB_Session()
    new_user_data = Results(searcher_id=user_id,
                            result_id=result_id,)
    db_session.add(new_user_data)
    db_session.commit()
    db_session.close()


def get_old_results(user_id: int):
    db_session = DB_Session()
    results = db_session.query(Results.result_id).filter(Results.searcher_id == user_id).all()
    results_ids = [i[0] for i in results]
    db_session.close()
    return results_ids


def change_info(redacted_user: VKUser):
    db_session = DB_Session()
    info = db_session.query(Users).filter(Users.id == redacted_user.id).all()[0]
    info.age = redacted_user.age
    info.sex = redacted_user.sex
    info.city = redacted_user.city
    info.city_id = redacted_user.city_id
    info.age_from = redacted_user.age_range[0]
    info.age_to = redacted_user.age_range[1]
    db_session.commit()
    db_session.close()
