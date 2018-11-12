; ModuleID = declares

declare i8* @"malloc"(i64 %".1")

declare void @"free"(i8* %".1")

declare i32 @"putchar"(i32 %".1")

declare i32 @"printf"(i8* %".1", ...)

declare i64 @"scanf"(i8* %".1", i64* %".2", ...)

declare i4 @"getchar"()

declare i32 @"puts"(i32* %".1")
