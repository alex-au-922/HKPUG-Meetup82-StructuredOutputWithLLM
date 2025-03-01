import { fetchEventSource } from "@microsoft/fetch-event-source"
import { useResumeStore, type WorkExperience } from "./useStore/useResumeStore"


function WorkExperienceCard({ workExp }: { workExp: WorkExperience }) {
  return (
    <div className="card bg-base-100 w-full shadow-xl mx-8 my-4 border-2 border-solid rounded-lg hover:shadow-2xl hover:cursor-pointer mt-4">
      <div className="card-body">
        <h2 className="card-title">{workExp.title}</h2>
        <p className="flex space-x-2 justify-between">
          <span>{workExp.company}</span>
          <span>{workExp.startDate} - {workExp.endDate || "present"}</span>
        </p>
        <p className="text-justify">{workExp.description}</p>
      </div>
    </div>
  )
}

function App() {
  const {
    resumeInput,
    setResumeInput,
    nativeBlockingWorkExps,
    nativeBlockingRequestDuration,
    instructorStreamingWorkExps,
    instructorStreamingRequestDuration,
    resetState,
    setNativeBlockingRequestDuration,
    setInstructorStreamingRequestDuration,
    appendInstructorStreamingWorkExps,
    appendNativeBlockingWorkExps 
  } = useResumeStore()

  const handleParse = async () => {
    resetState();
    await Promise.all([
      handleParseNativeBlocking(),
      handleParseInstructorStreaming(),
    ])
  }

  const handleParseNativeBlocking = async () => {
    const response = await fetch(import.meta.env.VITE_NATIVE_BLOCKING_API, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text: resumeInput }),
    });
    const data = await response.json();
    console.log(`Native blocking response: ${JSON.stringify(data)}`);
    setNativeBlockingRequestDuration(new Date());
    for (const workExp of data) {
      appendNativeBlockingWorkExps(workExp);
    }
  }
  const handleParseInstructorStreaming = async () => {
    const ctrl = new AbortController();
    await fetchEventSource(import.meta.env.VITE_INSTRUCTOR_STREAMING_API, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            text: resumeInput,
        }),
        signal: ctrl.signal,
        async onopen(response) {
          if (response.ok && response.status === 200) {
            console.log('Connection established');
            return;
          }
          throw new Error('Connection failed');
        },
        onmessage(event) {
          if (useResumeStore.getState().instructorStreamingWorkExps.length === 0) {
            setInstructorStreamingRequestDuration(new Date());
          }
          const data = JSON.parse(event.data);
          console.log(`Instructor streaming response: ${JSON.stringify(data)}`);
          appendInstructorStreamingWorkExps(data);
        },
        onerror(error) {
          console.error('Error:', error);
          ctrl.abort();
        },
        onclose() {
          console.log('Connection closed');
          ctrl.abort();
        }
    });
  }

  const round = (num: number, decimalPlaces: number) => {
    const factor = Math.pow(10, decimalPlaces);
    return Math.round(num * factor) / factor;
  }

  return (
    <div className="container mx-auto m-4 w-full mb-8">
      <div className="flex flex-col space-y-4">
        <h1 className="justify-center text-center text-4xl">Resume Work Experience Extractor</h1>
        <textarea
          className="w-3/4 h-96 mb-8 mt-4 mx-auto rounded-lg shadow-lg placeholder:text-gray-500 placeholder:italic border-solid border-1"
          value={resumeInput}
          onChange={(e) => setResumeInput(e.target.value)}
          placeholder="Paste your resume here"
        />
        <button className="btn btn-accent p-4 w-fit mx-auto" onClick={handleParse}>Parse</button>
      </div>
      <div className="flex space-x-8 mt-8">
        <div className="flex-1 flex flex-col">
          <h2 className="text-center">Native Blocking</h2>
          <p className="relative"><span className="absolute small italic text-gray-500 right-0">Time-to-first-byte (TTFB): {round(nativeBlockingRequestDuration, 2)}s</span></p>
          <div className="mt-4">
          {nativeBlockingWorkExps.map((workExp) => (
            <WorkExperienceCard key={workExp.title} workExp={workExp} />
          ))}
          </div>
        </div>
        <div className="flex-1 flex flex-col">
          <h2 className="text-center">Instructor Streaming</h2>
          <p className="relative"><span className="absolute small italic text-gray-500 right-0">Time-to-first-byte (TTFB): {round(instructorStreamingRequestDuration,2)}s</span></p>
          <div className="mt-4">
          {instructorStreamingWorkExps.map((workExp) => (
            <WorkExperienceCard key={workExp.title} workExp={workExp} />
          ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
