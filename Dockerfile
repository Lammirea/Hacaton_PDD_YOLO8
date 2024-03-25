FROM python:3.11

EXPOSE 8085
#
WORKDIR /code
RUN python3 -m venv venv
RUN chmod u+x ./venv/bin/activate
RUN ./venv/bin/activate
#
COPY ./ /code/app
COPY ./requirements.txt /code/requirements.txt
#
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

#

#
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]