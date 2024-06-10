#* base image
FROM dalmeng/base_judger_image:1.0.0

#* work directory setting
WORKDIR /usr/src/app

#* copy project file
COPY . .

#* check if all programming lanaguages are installed
RUN python3 --version
RUN gcc --version
RUN g++ --version
RUN java -version

#* install env
RUN pip3 install -r requirements.txt

#* port open
EXPOSE 8004

#* set env file and run server
RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]