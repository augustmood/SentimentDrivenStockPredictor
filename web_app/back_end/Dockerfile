FROM --platform=arm64 python:3.11

RUN python -m pip install --upgrade pip

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /back_end
WORKDIR /back_end
COPY requirements.txt /back_end/
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]