from ast import FunctionDef
from decimal import Decimal
from sqlite3 import IntegrityError
from sqlalchemy.orm import sessionmaker
from model.training import AthleteGoal, Multimedia, TrainingPlan
from typing import List
from model.training import UserFavoriteTrainingPlan, PlanReview, UserTraining
from fastapi import HTTPException
import requests
from constants import BLOCKED_STATE, ACTIVE_STATE
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from sqlalchemy import func, or_, extract
from decimal import Decimal
import random
import re


class TrainingDal:

    def __init__(self, engine):
        self.engine = engine
        self.Session = sessionmaker(bind=self.engine)

    def get_training_plan_by_id(self, training_id, skip_blocked: bool = True) -> TrainingPlan:
        training_plan = None
        with self.Session() as session:
            try:
                if skip_blocked:
                    training_plan = session.query(TrainingPlan).filter(
                        TrainingPlan.id == training_id).filter(
                        TrainingPlan.state == ACTIVE_STATE).first()
                else:
                    training_plan = session.query(TrainingPlan).filter(
                        TrainingPlan.id == training_id).first()
            except SQLAlchemyError as e:
                raise HTTPException(
                    status_code=404, detail="Training plan not found")

            if not training_plan:
                raise HTTPException(
                    status_code=404, detail="Training plan not found")
            return training_plan

    def get_trainings(self, training_type: str, difficulty: str, trainer_id: int, skip_blocked: bool = True) -> List[TrainingPlan]:
        with self.Session() as session:
            try:
                query = session.query(TrainingPlan)
                if training_type is not None:
                    query = query.filter(TrainingPlan.type == training_type)
                if difficulty is not None:
                    query = query.filter(TrainingPlan.difficulty == difficulty)
                if trainer_id is not None:
                    query = query.filter(TrainingPlan.trainerId == trainer_id)

                if skip_blocked:
                    query = query.filter(TrainingPlan.state == ACTIVE_STATE)
                return query.all()
            except SQLAlchemyError as e:
                return []

    def valid_name(self, name: str):
        if not name or len(name) < 3 or len(name) > 50:
            raise HTTPException(
                status_code=400, detail="El nombre debe tener entre 3 y 50 caracteres")
    
    def valid_description(self, description: str):
        if not description or len(description) < 10 or len(description) > 100:
            raise HTTPException(
                status_code=400, detail="La descripción debe tener entre 10 y 100 caracteres")
    def valid_schedule(self, start: str, end: str):
        start_split = start.split(":")
        end_split = end.split(":")
        if len(start_split[0]) != 2 or len(start_split[1]) != 2 or len(end_split[0]) != 2 or len(end_split[1]) != 2 or len(start_split) != 2 or len(end_split) != 2:
            raise HTTPException(
                status_code=400, detail="Comienzo y fin deben estar en formato HH:MM")
        if int(start_split[0]) > 23 or int(start_split[1]) > 59 or int(end_split[0]) > 23 or int(end_split[1]) > 59:
            raise HTTPException(
                status_code=401, detail="Hora inválida")
        if int(start_split[0]) > int(end_split[0]) or (int(start_split[0]) == int(end_split[0]) and int(start_split[1]) > int(end_split[1])):
            raise HTTPException(
                status_code=402, detail="La hora de inicio debe ser anterior a la hora de fin")

    def valid_days(self, days: str):
        if days is not None:
            days = days.split(",")
            for day in days:
                if day.lower().strip() not in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]:
                    raise HTTPException(
                        status_code=400, detail="día invalido")
            if len(days) != len(set(days)):
                raise HTTPException(
                    status_code=400, detail="los dias deben ser únicos")

    def valid_interval(self, param: str, number: int, min: int, max: int):
        if number < min or number > max:
            raise HTTPException(
                status_code=400, detail=f"{param} debe estar entre {min} y {max}")

    def create_training(self, training: TrainingPlan):
        return TrainingPlan(
            title=training.title,
            description=training.description,
            state=training.state,
            difficulty=training.difficulty,
            type=training.type,
            trainerId=training.trainerId,
            location=training.location,
            latitude=training.latitude,
            longitude=training.longitude,
            start=training.start,
            end=training.end,
            days=training.days
        )

    def add_training(self, training: TrainingPlan):
        with self.Session() as session:
            try:
                if training.trainerId is None or training.title is None or training.type is None or training.difficulty is None or training.location is None or training.start is None or training.end is None or training.days is None or training.latitude is None or training.longitude is None:
                    raise HTTPException(
                        status_code=400, detail="Faltan campos obligatorios (trainerId, titulo, tipo, dificultad, localización, inicio, fin, días, latitud o longitud)")

                self.valid_name(training.title)
                self.valid_description(training.description)
                self.valid_schedule(training.start, training.end)

                self.valid_days(training.days)

                self.valid_interval("difficulty", training.difficulty, 1, 10)

                training = self.create_training(training)

                session.add(training)
                session.commit()
                session.refresh(training)
                return training
            except Exception as e:
                session.rollback()
                if e.detail:
                    raise e
                raise HTTPException(
                    status_code=500, detail="Falta algún campo obligatorio")

    def update_training(self, newtraining: TrainingPlan):
        with self.Session() as session:
            self.valid_schedule(newtraining.start, newtraining.end)
            self.valid_days(newtraining.days)
            self.valid_interval("difficulty", newtraining.difficulty, 1, 10)

            try:
                session.query(TrainingPlan).filter(TrainingPlan.id == newtraining.id).update({
                    TrainingPlan.title: newtraining.title,
                    TrainingPlan.description: newtraining.description,
                    TrainingPlan.state: newtraining.state,
                    TrainingPlan.difficulty: newtraining.difficulty,
                    TrainingPlan.type: newtraining.type,
                    TrainingPlan.trainerId: newtraining.trainerId,
                    TrainingPlan.location: newtraining.location,
                    TrainingPlan.latitude: newtraining.latitude,
                    TrainingPlan.longitude: newtraining.longitude,
                    TrainingPlan.start: newtraining.start,
                    TrainingPlan.end: newtraining.end,
                    TrainingPlan.days: newtraining.days
                })
                session.commit()
                updated_training = session.query(TrainingPlan).filter(
                    TrainingPlan.id == newtraining.id).first()
                return updated_training

            except Exception as e:
                session.rollback()
                raise HTTPException(
                    status_code=500, detail="Falta algún campo obligatorio")

    def get_training_by_hours(self, start: str, end: str):
        with self.Session() as session:
            if not start or not end:
                raise HTTPException(
                    status_code=401, detail="Faltan campos obligatorios (comienzo o fin)")

            self.valid_schedule(start, end)

            trainings = session.query(TrainingPlan).filter(
                TrainingPlan.start >= start).filter(
                TrainingPlan.end <= end).all()
            if not trainings:
                return []
            return [training.as_dict() for training in trainings]

    def get_training_by_days(self, days: str):
        with self.Session() as session:
            if not days:
                raise HTTPException(
                    status_code=401, detail="Faltan campos obligatorios (dias)")

            self.valid_days(days)

            trainings = session.query(TrainingPlan).filter(
                or_(*
                    [TrainingPlan.days.ilike(f"%{day.lower().strip()}%") for day in days])
            ).all()

            if not trainings:
                return []
            return [training.as_dict() for training in trainings]

    def get_training_by_days_and_hours(self, days: str, start: str, end: str):
        with self.Session() as session:
            if not days or not start or not end:
                raise HTTPException(
                    status_code=401, detail="Faltan campos obligatorios (dias, comienzo o fin)")

            self.valid_schedule(start, end)
            self.valid_days(days)

            trainings = session.query(TrainingPlan).filter(
                TrainingPlan.days.in_(days)).filter(
                TrainingPlan.start >= start).filter(
                TrainingPlan.end <= end).all()
            if not trainings:
                return []
            return [training.as_dict() for training in trainings]

    def add_training_to_favorite(self, training_id: int, user_id: int):
        with self.Session() as session:
            try:

                if not user_id or not training_id:
                    raise HTTPException(
                        status_code=400, detail="Faltan campos obligatorios (user_id o training_id)")

                self.check_if_user_exists(user_id)

                user_favorite_training_plan = UserFavoriteTrainingPlan(
                    userId=user_id, trainingPlanId=training_id)
                session.add(user_favorite_training_plan)
                session.commit()
                session.refresh(user_favorite_training_plan)
                return user_favorite_training_plan
            except IntegrityError:
                session.rollback()
                raise HTTPException(
                    status_code=404, detail="User or training not found")
            except:
                session.rollback()
                raise HTTPException(
                    status_code=500, detail="Something went wrong")

    def delete_training(self, training_id: int):
        with self.Session() as session:
            try:
                training = session.query(TrainingPlan).filter(
                    TrainingPlan.id == training_id).first()
                session.delete(training)
                session.commit()
                return training
            except IntegrityError:
                session.rollback()
                raise HTTPException(
                    status_code=404, detail="Training not found")
            except Exception as e:
                session.rollback()
                raise HTTPException(
                    status_code=500, detail=f"Something went wrong: {e}")

    def delete_training_from_favorite(self, training_id: int, user_id: int):
        print(f"deleting training {training_id} from user {user_id}")
        with self.Session() as session:
            try:
                self.check_if_user_exists(user_id)
                user_favorite_training_plan = session.query(UserFavoriteTrainingPlan).filter(
                    UserFavoriteTrainingPlan.userId == user_id).filter(
                    UserFavoriteTrainingPlan.trainingPlanId == training_id).first()
                session.delete(user_favorite_training_plan)
                session.commit()
                return user_favorite_training_plan
            except IntegrityError:
                session.rollback()
                raise HTTPException(
                    status_code=404, detail="User or training not found")

    def get_favorite_trainings(self, user_id: int):
        with self.Session() as session:
            self.check_if_user_exists(user_id)
            trainings = session.query(TrainingPlan).join(UserFavoriteTrainingPlan, UserFavoriteTrainingPlan.trainingPlanId == TrainingPlan.id) \
                .filter(UserFavoriteTrainingPlan.userId == user_id) \
                .filter(TrainingPlan.state == ACTIVE_STATE).all()
            if not trainings:
                return []
            return [training.as_dict() for training in trainings]

    def check_if_user_exists(self, user_id: int):
        user_service_url = f"http://user-service:80/api/users/{user_id}"
        response = requests.get(user_service_url, headers={
            "test": "true",
            "dev": "true"})
        if response.status_code != 200:
            raise HTTPException(
                status_code=404, detail="User not found")

    def add_training_review(self, training_plan_id: int, user_id: int, score: int, comment: str = None):
        with self.Session() as session:
            try:

                if not user_id or not training_plan_id or not score:
                    raise HTTPException(
                        status_code=400, detail="Faltn campos obligatorios (user_id, training_plan_id o score)")

                self.valid_interval("Score", score, 1, 5)

                if session.query(TrainingPlan).filter(TrainingPlan.id == training_plan_id).count() == 0:
                    raise HTTPException(
                        status_code=404, detail="Training plan not found")

                self.check_if_user_exists(user_id)

                if session.query(PlanReview).filter(PlanReview.userId == user_id).filter(PlanReview.trainingPlanId == training_plan_id).count() > 0:
                    raise HTTPException(
                        status_code=408, detail="Ya has realizado una valoración de este plan de entrenamiento")

                training_plan = session.query(TrainingPlan).filter(
                    TrainingPlan.id == training_plan_id).first()
                if training_plan.trainerId == user_id:
                    raise HTTPException(
                        status_code=409, detail="No puedes valorar tus propios planes de entrenamiento")

                training_review = PlanReview(
                    userId=user_id, score=score, comment=comment, trainingPlanId=training_plan_id)
                session.add(training_review)
                session.commit()
                session.refresh(training_review)
                return training_review
            except HTTPException as e:
                session.rollback()
                raise HTTPException(
                    status_code=e.status_code, detail=e.detail)
            except:
                session.rollback()
                raise HTTPException(
                    status_code=500, detail="Something went wrong")


    def add_training_image(self, training_plan_id: int, url: str):
        with self.Session() as session:
            try:
                if session.query(TrainingPlan).filter(TrainingPlan.id == training_plan_id).count() == 0:
                    raise HTTPException(
                        status_code=404, detail="Training plan not found")

                multimedia = Multimedia(
                    fileUrl=url, type="image/*", trainingPlanId=training_plan_id)
                session.add(multimedia)
                session.commit()
                session.refresh(multimedia)
                return multimedia
            except HTTPException as e:
                session.rollback()
                raise HTTPException(
                    status_code=e.status_code, detail=e.detail)
            except:
                session.rollback()
                raise HTTPException(
                    status_code=500, detail="Something went wrong")
            
    def get_training_images(self, training_plan_id: int):
        with self.Session() as session:
            if session.query(TrainingPlan).filter(TrainingPlan.id == training_plan_id).count() == 0:
                raise HTTPException(
                    status_code=404, detail="Training plan not found")
            images = session.query(Multimedia).filter(
                Multimedia.trainingPlanId == training_plan_id).all()
            if not images:
                return []
            return [image.as_dict() for image in images]

    def get_training_reviews(self, training_plan_id: int):
        with self.Session() as session:
            if session.query(TrainingPlan).filter(TrainingPlan.id == training_plan_id).count() == 0:
                raise HTTPException(
                    status_code=404, detail="Training plan not found")
            reviews = session.query(PlanReview).filter(
                PlanReview.trainingPlanId == training_plan_id).all()
            if not reviews:
                return []
            return [review.as_dict() for review in reviews]

    def valid_duration(self, duration: str):
        duration_split = duration.split(":")
        if (len(duration_split) < 3):
            raise HTTPException(
                status_code=400, detail="El formato debe ser HH:MM:SS")
        
        if len(duration_split[0]) != 2 or len(duration_split[1]) != 2 or len(duration_split[2]) != 2:
            raise HTTPException(
                status_code=400, detail="El formato debe ser HH:MM:SS")

        if int(duration_split[0]) < 0 or int(duration_split[1]) < 0 or int(duration_split[2]) < 0:
            raise HTTPException(
                status_code=400, detail="La duracion debe ser positiva")

    def add_user_training(self, user_id: int, training_plan_id: int, distance: float, duration: float, steps: int, calories: int, date: datetime):
        with self.Session() as session:
            try:
                if (distance is None or duration is None or steps is None or calories is None or date is None) and not (distance == 0 or duration == 0 or steps == 0 or calories == 0 or date == 0):
                    raise HTTPException(
                        status_code=400, detail="Faltan datos obligatorios (distancia, duración, pasos, calorías o fecha)") 
                date_received = date.replace(tzinfo=None)
                if date_received > datetime.now().replace(tzinfo=None):
                    raise HTTPException(
                        status_code=400, detail="La fecha no puede ser posterior a la actual")

                if distance < 0 or steps < 0 or calories < 0:
                    raise HTTPException(
                        status_code=400, detail="La distancia, pasos y calorías deben ser positivos")
                print("ANTES DE VALID DURATION")
                self.valid_duration(duration)
                print("DESPUES DE VALID DURATION")

                user_training = UserTraining(userId=user_id, trainingPlanId=training_plan_id,
                                             distance=distance, duration=duration, steps=steps, calories=calories, date=date)
                session.add(user_training)
                session.commit()
                session.refresh(user_training)
                return user_training
            except HTTPException as e:
                session.rollback()
                raise HTTPException(
                    status_code=e.status_code, detail=e.detail)
            except Exception as e:
                session.rollback()
                raise HTTPException(
                    status_code=500, detail=f"Something went wrong: {e}")
            
    def get_user_trainings_for_user_count(self, user_id: int):
        with self.Session() as session:
            user_trainings = session.query(UserTraining).filter(
                UserTraining.userId == user_id).count()
            return user_trainings

    def calculate_duration(self, session, user_id, start=None, end=None, avg=False):
        if start and end:
            duration_query = session.query(
                UserTraining.duration).filter(UserTraining.userId == user_id).filter(UserTraining.date >= start).filter(UserTraining.date <= end)

        else:
            duration_query = session.query(
                UserTraining.duration).filter(UserTraining.userId == user_id)

        durations = 0
        for duration in duration_query.all():
            duration_split = duration[0].split(":")
            durations += int(duration_split[0]) * 3600 + \
                int(duration_split[1]) * 60 + int(duration_split[2])

        if avg:
            return str(timedelta(seconds=durations / duration_query.count()))
        else:
            return str(timedelta(seconds=durations))

    def get_user_training_average(self, user_id: int):
        with self.Session() as session:
            user_service_url = f"http://user-service:80/api/users/{user_id}"
            response = requests.get(user_service_url, headers={
                "test": "true",
                "dev": "true"})
            if response.status_code != 200:
                raise HTTPException(
                    status_code=404, detail="User not found")

            user_training_query = session.query(
                func.avg(UserTraining.distance),
                func.avg(UserTraining.steps),
                func.avg(UserTraining.calories)
            ).filter(UserTraining.userId == user_id)

            user_training_averages = user_training_query.first()

            if not user_training_averages[0]:
                return {
                    "distance": 0,
                    "duration": "00:00:00",
                    "steps": 0,
                    "calories": 0
                }

            avg_duration = self.calculate_duration(
                session, user_id, None, None, True)

            return {
                "distance": float(user_training_averages[0] or 0),
                "duration": avg_duration,
                "steps": float(user_training_averages[1] or 0),
                "calories": float(user_training_averages[2] or 0)
            }

    def get_user_training_total(self, user_id: int):
        with self.Session() as session:
            user_service_url = f"http://user-service:80/api/users/{user_id}"
            response = requests.get(user_service_url, headers={
                "test": "true",
                "dev": "true"})
            if response.status_code != 200:
                raise HTTPException(
                    status_code=404, detail="User not found")

            user_training_query = session.query(
                func.sum(UserTraining.distance),
                func.sum(UserTraining.steps),
                func.sum(UserTraining.calories)
            ).filter(UserTraining.userId == user_id)

            user_training_totals = user_training_query.first()

            if not user_training_totals[0]:
                return {
                    "distance": 0,
                    "duration": "00:00:00",
                    "steps": 0,
                    "calories": 0
                }

            total_duration = self.calculate_duration(
                session, user_id, None, None, False)

            return {
                "distance": float(user_training_totals[0] or 0),
                "duration": total_duration,
                "steps": float(user_training_totals[1] or 0),
                "calories": float(user_training_totals[2] or 0)
            }

    def get_user_trainings_of_training_plan(self, user_id: int, training_plan_id):
        with self.Session() as session:
            user_trainings = session.query(UserTraining).filter(
                UserTraining.userId == user_id).filter(UserTraining.trainingPlanId == training_plan_id).all()
            if not user_trainings:
                return []
            return [training.as_dict() for training in user_trainings]


    def get_user_trainings(self, user_id: int):
        with self.Session() as session:
            user_trainings = session.query(UserTraining).filter(
                UserTraining.userId == user_id).all()
            if not user_trainings:
                return []

            return [training.as_dict() for training in user_trainings]


    def get_user_trainings_between_dates(self, user_id: int, start: datetime, end: datetime):
        with self.Session() as session:
            if not start or not end:
                raise HTTPException(
                    status_code=401, detail="Faltan campos obligatorios (comienzo o fin)")

            if start > end:
                raise HTTPException(
                    status_code=400, detail="La fecha de inicio debe ser anterior a la fecha de fin")

            user_trainings = session.query(UserTraining).filter(
                UserTraining.userId == user_id).filter(UserTraining.date >= start).filter(UserTraining.date <= end).all()
            if not user_trainings:
                return []
            return [training.as_dict() for training in user_trainings]

    def get_user_training_total_between_dates(self, user_id: int, start: datetime, end: datetime):
        with self.Session() as session:
            if not start or not end:
                raise HTTPException(
                    status_code=401, detail="Faltan campos obligatorios (comienzo o fin)")

            if start > end:
                raise HTTPException(
                    status_code=400, detail="La fecha de inicio debe ser anterior a la fecha de fin")

            user_training_query = session.query(
                func.sum(UserTraining.distance),
                func.sum(UserTraining.steps),
                func.sum(UserTraining.calories)
            ).filter(UserTraining.userId == user_id).filter(UserTraining.date >= start).filter(UserTraining.date <= end)

            user_training_totals = user_training_query.first()

            if not user_training_totals[0]:
                return {
                    "distance": 0,
                    "duration": "00:00:00",
                    "steps": 0,
                    "calories": 0
                }

            total_duration = self.calculate_duration(
                session, user_id, start, end, False)

            return {
                "distance": float(user_training_totals[0] or 0),
                "duration": total_duration,
                "steps": float(user_training_totals[1] or 0),
                "calories": float(user_training_totals[2] or 0)
            }



    def query_for_days(self, session, user_id, start, end):
        query = session.query(
            func.concat(extract('day', UserTraining.date), "-", extract("month", UserTraining.date), "-", extract("year", UserTraining.date)).label('day'),
            func.sum(UserTraining.distance).label("distance"),
            func.sum(UserTraining.steps).label("steps"),
            func.sum(UserTraining.calories).label("calories")
        ).filter(
            UserTraining.userId == user_id,
            UserTraining.date >= start,
            UserTraining.date <= end
        ).group_by(
            extract('day', UserTraining.date),
            extract('month', UserTraining.date),
            extract("year", UserTraining.date)
        )
        return query
    
    def query_for_weeks(self, session, user_id, start, end):
        query = session.query(
            func.concat(extract('week', UserTraining.date), "-", extract("year", UserTraining.date)).label('week'),
            func.sum(UserTraining.distance).label("distance"),
            func.sum(UserTraining.steps).label("steps"),
            func.sum(UserTraining.calories).label("calories")
        ).filter(
            UserTraining.userId == user_id,
            UserTraining.date >= start,
            UserTraining.date <= end
        ).group_by(
            extract('week', UserTraining.date),
            extract("year", UserTraining.date)
        )
        return query
    
    def query_for_months(self, session, user_id, start, end):
        query = session.query(
            func.concat(extract('month', UserTraining.date), "-", extract("year", UserTraining.date)).label('month'),
            func.sum(UserTraining.distance).label("distance"),
            func.sum(UserTraining.steps).label("steps"),
            func.sum(UserTraining.calories).label("calories")
        ).filter(
            UserTraining.userId == user_id,
            UserTraining.date >= start,
            UserTraining.date <= end
        ).group_by(
            extract('month', UserTraining.date),
            extract("year", UserTraining.date)
        )
        return query
    
    def query_for_years(self, session, user_id, start, end):
        query = session.query(
            func.concat(extract("year", UserTraining.date)).label('year'),
            func.sum(UserTraining.distance).label("distance"),
            func.sum(UserTraining.steps).label("steps"),
            func.sum(UserTraining.calories).label("calories")
        ).filter(
            UserTraining.userId == user_id,
            UserTraining.date >= start,
            UserTraining.date <= end
        ).group_by(
            extract("year", UserTraining.date)
        )
        return query


    def get_query_group_by(self, group_by: str, session, user_id, start, end):
        if group_by == "day":
            query = self.query_for_days(session, user_id, start, end)
        elif group_by == "week":
            query = self.query_for_weeks(session, user_id, start, end)
        elif group_by == "month":
            query = self.query_for_months(session, user_id, start, end)
        elif group_by == "year":
            query = self.query_for_years(session, user_id, start, end)
        else:
            raise HTTPException(
                status_code=400, detail="Invalid value for grouping")
        
        return query


    def get_user_training_total_between_dates_group_by(self, group_by: str, user_id: int, start: datetime, end: datetime):
        with self.Session() as session:
            if not start or not end:
                raise HTTPException(
                    status_code=401, detail="Faltan campos obligatorios (comienzo o fin)")

            if start > end:
                raise HTTPException(
                    status_code=400, detail="La fecha de inicio debe ser anterior a la fecha de fin")

            start_str = start.strftime("%Y-%m-%dT%H:%M:%SZ")
            end_str = end.strftime("%Y-%m-%dT%H:%M:%SZ")

            query = self.get_query_group_by(group_by, session, user_id, start_str, end_str)

            results = query.all()

            results_dict = {
                "label": [],
                "distance": [],
                "steps": [],
                "calories": []
            }

            for row in results:
                results_dict["label"].append(getattr(row, group_by))
                results_dict["distance"].append(row.distance)
                results_dict["steps"].append(row.steps)
                results_dict["calories"].append(row.calories)

            return results_dict
        
    def get_trainings_by_keyword(self, session, keyword):
        print(f"Getting trainings for keyword: {keyword}")
        query = session.query(TrainingPlan)
        query = query.filter(TrainingPlan.name.ilike(f"%{keyword}%"))
        return query.limit(2).all()


    def filter_repeated(self, trainings):
        res = []
        for t in trainings:
            t_dic = t.as_dict()
            exists = False
            for training in res:
                if t_dic["id"] == training["id"]:
                    exists = True
                
            if not exists:
                res.append(t_dic)
        
        return res

    def get_trainings_within_filters(self, training_type, min_difficulty, max_difficulty, keywords):
        with self.Session() as session:
            query = session.query(TrainingPlan)
            query = query.filter(TrainingPlan.type == training_type)
            query = query.filter(TrainingPlan.difficulty >= min_difficulty).filter(TrainingPlan.difficulty <= max_difficulty)
            res = query.limit(10).all()
            print(f"Res: {res}")
            try:
                res_keyword_1 = self.get_trainings_by_keyword(session, training_type, random.choice(keywords))
                res_keyword_2 = self.get_trainings_by_keyword(session, training_type, random.choice(keywords))
                res_keyword_3 = self.get_trainings_by_keyword(session, training_type, random.choice(keywords))
                res = res + res_keyword_1 + res_keyword_2 + res_keyword_3
                print(f"Res with keywords: {res}" )
            except Exception as e:
                print(f"Failed getting trainings by keyword: {e}")

            res_filtered = self.filter_repeated(res)
            return res_filtered


    def create_athlete_goal(self, title: str, description: str, type: str, metric: str, athlete_id: int):
        with self.Session() as session:
            self.check_if_user_exists(athlete_id)

            if title is None or type is None or description is None or metric is None:
                raise HTTPException(
                    status_code=400, detail="Faltan campos obligatorios (titulo, tipo, metrica o descripción)")
            
            if metric < 0:
                raise HTTPException(
                    status_code=400, detail="La métrica debe ser positiva")
            
            if type not in ["Calorias", "Pasos", "Distancia"]:
                raise HTTPException(
                    status_code=400, detail="Tipo de objetivo inválido: (Calorias, Pasos, Distancia))")

            new_athlete_goal = AthleteGoal(
                title=title,
                description=description,
                type=type,
                metric=metric,
                athleteId=athlete_id,
                achieved=False,
                lastAchieved=None         
            )

            session.add(new_athlete_goal)
            session.commit()
            session.refresh(new_athlete_goal)
            return new_athlete_goal

    def get_athlete_goals(self, athlete_id: int):
        with self.Session() as session:
            self.check_if_user_exists(athlete_id)
            goals = session.query(AthleteGoal).filter(
                AthleteGoal.athleteId == athlete_id).all()
            
            if not goals:
                return []
            
            goals = [goal.as_dict() for goal in goals]

            for goal in goals:
                goal["multimedia"] = []
                multimedia = session.query(Multimedia).filter(
                    Multimedia.athleteGoalId == goal["id"]).all()
                if multimedia:
                    goal["multimedia"] = [m.as_dict()["fileUrl"] for m in multimedia]

                
            return goals


    def check_if_athlete_goal_exists(self, goal_id: int):
        with self.Session() as session:
            athlete = session.query(AthleteGoal).filter(AthleteGoal.id == goal_id).first()
            if not athlete:    
                raise HTTPException(
                    status_code=404, detail="Objetivo no encontrado")
            else:
                return athlete


    def delete_athelete_goal(self, goal_id: int):
        with self.Session() as session:
            goal = self.check_if_athlete_goal_exists(goal_id)
            session.delete(goal)
            session.commit()
            return goal
        

    def validate_date_time(self, date_time_string: str):
        pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
        if re.match(pattern, date_time_string):
            return True
        else:
            return False
    
    def update_athlete_goal(self, goal_id: int, title: str, description: str, type: str, metric: str, achieved: bool):
        with self.Session() as session:
            goal = self.check_if_athlete_goal_exists(goal_id)

            if title is None or type is None or description is None or metric is None:
                raise HTTPException(
                    status_code=400, detail="Faltan campos obligatorios (titulo, tipo, metrica o descripción)")

            if metric < 0:
                raise HTTPException(
                    status_code=400, detail="La métrica debe ser positiva")
            
                        
            if type and type not in ["Calorias", "Pasos", "Distancia"]:
                raise HTTPException(
                    status_code=400, detail="Tipo de objetivo inválido: (Calorias, Pasos, Distancia))")
            

            session.query(AthleteGoal).filter(AthleteGoal.id == goal_id).update({
                AthleteGoal.title: title,
                AthleteGoal.description: description,
                AthleteGoal.type: type,
                AthleteGoal.metric: metric
            })
            session.commit()

            updated_goal = session.query(AthleteGoal).filter(
                AthleteGoal.id == goal_id).first()
            return updated_goal
        
    def achieve_athlete_goal(self, goal_id: int):
        with self.Session() as session:
            goal = self.check_if_athlete_goal_exists(goal_id)
            session.query(AthleteGoal).filter(AthleteGoal.id == goal_id).update({
                AthleteGoal.achieved: True,
                AthleteGoal.lastAchieved: datetime.now()
            })
            session.commit()

            updated_goal = session.query(AthleteGoal).filter(
                AthleteGoal.id == goal_id).first()
            return updated_goal

            
        
    def add_multimedia_to_athlete_goal(self, goal_id: int, url: str):
        with self.Session() as session:
            goal = self.check_if_athlete_goal_exists(goal_id)
            
            multimedia = Multimedia(
                fileUrl=url, type="image/*", athleteGoalId=goal_id)
            session.add(multimedia)
            session.commit()
            session.refresh(multimedia)
            return multimedia
        

    def get_athlete_goal_by_id(self, goal_id: int):
        with self.Session() as session:
            goal = self.check_if_athlete_goal_exists(goal_id)
            return goal.as_dict()