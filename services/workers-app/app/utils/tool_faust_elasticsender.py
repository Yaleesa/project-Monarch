import faust

app = faust.App('testing', broker='kafka://localhost:29092')
unit_topic = app.topic('module-tests')
#
@app.agent(unit_topic)
async def send_test(testsss):
    async for test in testsss:
        print(test)

unit_topic.send(value={"jemoeder":"enzo"})

if __name__ == '__main__':
    app.main()
