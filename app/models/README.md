1️⃣ Таблицы и их логика
1. User — Пользователи
class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(32))
    last_name: Mapped[str] = mapped_column(String(32))
    username: Mapped[str] = mapped_column(String(32), unique=True)
    progress: Mapped[list['UserCourseProgress']] = relationship(
        "UserCourseProgress", back_populates="user"
    )
    is_active: Mapped[bool] = mapped_column(default=True)


id — уникальный идентификатор пользователя.

progress — список объектов UserCourseProgress. Связь One-to-Many: один пользователь может проходить много курсов.

is_active — статус активности пользователя.

Каждый элемент progress показывает конкретный курс, который проходит пользователь, и его текущий шаг в курсе.

2. Course — Курсы
class Course(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(32), unique=True)
    description: Mapped[str] = mapped_column(String(150), nullable=True)
    progress: Mapped[list['UserCourseProgress']] = relationship(
        "UserCourseProgress", back_populates="course"
    )
    steps: Mapped[list["Step"]] = relationship(back_populates="course")
    is_active: Mapped[bool] = mapped_column(default=True)


id — уникальный идентификатор курса.

progress — список прогресса пользователей на этом курсе (One-to-Many).

steps — список шагов курса (One-to-Many).

is_active — флаг активности курса.

Через progress можно узнать, какие пользователи проходят курс и на каком шаге они находятся.

3. Step — Шаги курса
class Step(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(32), unique=True)
    text_content: Mapped[Text] = mapped_column(nullable=True)
    image_url: Mapped[str] = mapped_column(nullable=True)
    course_id: Mapped['Course'] = mapped_column(ForeignKey('courses.id'))
    course: Mapped['Course'] = relationship(back_populates="steps")
    is_active: Mapped[bool] = mapped_column(default=True)
    is_end: Mapped[bool] = mapped_column(default=False)


course_id — внешний ключ на курс.

course — объект курса (Many-to-One: много шагов → один курс).

is_end — флаг, указывающий, что шаг финальный.

4. UserCourseProgress — Прогресс пользователя
class UserCourseProgress(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), primary_key=True)
    current_step_id: Mapped[int] = mapped_column(ForeignKey("steps.id"), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="progress")
    course: Mapped["Course"] = relationship("Course", back_populates="progress")
    current_step: Mapped["Step"] = relationship("Step")


user_id + course_id — составной первичный ключ.

Уникально идентифицирует прогресс пользователя по конкретному курсу.

current_step_id — внешний ключ на шаг, где находится пользователь.

user и course — объекты пользователя и курса (Many-to-One).

current_step — объект текущего шага (Many-to-One).

Это таблица связи Many-to-Many с дополнительными данными (current_step) — часто называется association table with extra fields.

2️⃣ Виды связей
| Откуда             | Куда               | Тип связи   | Комментарий                                 |
| ------------------ | ------------------ | ----------- | ------------------------------------------- |
| User               | UserCourseProgress | One-to-Many | Один пользователь → много прогрессов        |
| Course             | UserCourseProgress | One-to-Many | Один курс → много пользователей в прогрессе |
| UserCourseProgress | Step               | Many-to-One | Прогресс → конкретный шаг                   |
| Course             | Step               | One-to-Many | Один курс → много шагов                     |

В итоге получается: пользователь может проходить много курсов, курс может проходить много пользователей, и для каждого курса мы храним текущий шаг пользователя.

3️⃣ Навигация через объекты

Чтобы получить все курсы пользователя:

for progress in user.progress:
    print(progress.course.title)


Чтобы узнать текущий шаг пользователя на конкретном курсе:

user_course_progress = session.query(UserCourseProgress).filter_by(user_id=user.id, course_id=course.id).first()
print(user_course_progress.current_step.title)


Чтобы получить всех пользователей, проходящих курс:

for progress in course.progress:
    print(progress.user.username)

4️⃣ Примечания

ForeignKey обеспечивает ссылочную целостность между таблицами.

relationship создаёт удобные объекты Python для навигации между таблицами.

Таблица UserCourseProgress заменяет старую Many-to-Many через secondary и позволяет хранить дополнительные данные (текущий шаг).

Все связи настроены через back_populates, что позволяет двунаправленную навигацию.