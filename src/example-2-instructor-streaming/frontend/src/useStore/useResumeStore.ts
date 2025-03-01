
import { create } from 'zustand';

export interface WorkExperience {
  title: string;
  company: string;
  startDate: string;
  endDate: string;
  description: string;
}

interface ResumeParserState {
  // Resume input
  resumeInput: string;
  setResumeInput: (input: string) => void;
  
  // Native blocking approach data
  nativeBlockingWorkExps: WorkExperience[];
  nativeBlockingRequestStartTime: Date;
  nativeBlockingRequestDuration: number;
  
  // Instructor streaming approach data
  instructorStreamingWorkExps: WorkExperience[];
  instructorStreamingRequestStartTime: Date;
  instructorStreamingRequestDuration: number;
  
  // Actions
  resetState: () => void;
  setNativeBlockingRequestDuration: (now: Date) => void;
  setInstructorStreamingRequestDuration: (now: Date) => void;
  appendNativeBlockingWorkExps: (workExp: WorkExperience) => void;
  appendInstructorStreamingWorkExps: (workExp: WorkExperience) => void;
}

export const useResumeStore = create<ResumeParserState>((set) => ({
  // Initial state
  resumeInput: '',
  setResumeInput: (input) => set({ resumeInput: input }),
  
  nativeBlockingWorkExps: [],
  nativeBlockingRequestStartTime: new Date(),
  nativeBlockingRequestDuration: 0,
  
  instructorStreamingWorkExps: [],
  instructorStreamingRequestStartTime: new Date(),
  instructorStreamingRequestDuration: 0,
  
  // Actions
  resetState: () => set({
    nativeBlockingWorkExps: [],
    instructorStreamingWorkExps: [],
    nativeBlockingRequestStartTime: new Date(),
    instructorStreamingRequestStartTime: new Date(),
    nativeBlockingRequestDuration: 0,
    instructorStreamingRequestDuration: 0,
  }),
  setNativeBlockingRequestDuration: (now) => set((state) => ({
    nativeBlockingRequestDuration: (now.getTime() - state.nativeBlockingRequestStartTime.getTime()) / 1000,
  })),
  setInstructorStreamingRequestDuration: (now) => set((state) => ({
    instructorStreamingRequestDuration: (now.getTime() - state.instructorStreamingRequestStartTime.getTime()) / 1000,
  })),
  appendNativeBlockingWorkExps: (workExps) => set((state) => ({
    nativeBlockingWorkExps: [...state.nativeBlockingWorkExps, workExps],
  })),
  appendInstructorStreamingWorkExps: (workExps) => set((state) => ({
    instructorStreamingWorkExps: [...state.instructorStreamingWorkExps, workExps],
  })),
}));