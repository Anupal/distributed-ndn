// Use throughout your app instead of plain `useDispatch` and `useSelector`
//This is for typed useDispatch and typed useSelector
import { TypedUseSelectorHook, useDispatch, useSelector } from "react-redux"
import { AppDispatch, RootState } from "../index"

export const useAppDispatch = () => useDispatch<AppDispatch>()
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector
