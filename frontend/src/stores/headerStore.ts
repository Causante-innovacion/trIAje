import { create } from 'zustand'
import { ReactNode } from 'react'

interface HeaderState {
    title: string | null
    rightContent: ReactNode | null
    setTitle: (title: string | null) => void
    setRightContent: (content: ReactNode | null) => void
    resetHeader: () => void
}

export const useHeaderStore = create<HeaderState>((set) => ({
    title: null,
    rightContent: null,
    setTitle: (title) => set({ title }),
    setRightContent: (content) => set({ rightContent: content }),
    resetHeader: () => set({ title: null, rightContent: null }),
}))
