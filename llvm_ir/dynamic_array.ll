; ModuleID = dynamic_array

%struct.Vector = type { i32, i32, i32* }

@.str = private unnamed_addr constant [46 x i8] c"Index %d out of bounds for vector of size %d\0A\00", align 1

; Function Attrs: nounwind uwtable
define void @vector_init(%struct.Vector* %vector) {
  %1 = alloca %struct.Vector*, align 8
  store %struct.Vector* %vector, %struct.Vector** %1, align 8
  %2 = load %struct.Vector*, %struct.Vector** %1, align 8
  %3 = getelementptr inbounds %struct.Vector, %struct.Vector* %2, i32 0, i32 0
  store i32 0, i32* %3, align 8
  %4 = load %struct.Vector*, %struct.Vector** %1, align 8
  %5 = getelementptr inbounds %struct.Vector, %struct.Vector* %4, i32 0, i32 1
  store i32 100, i32* %5, align 4
  %6 = load %struct.Vector*, %struct.Vector** %1, align 8
  %7 = getelementptr inbounds %struct.Vector, %struct.Vector* %6, i32 0, i32 1
  %8 = load i32, i32* %7, align 4
  %9 = sext i32 %8 to i64
  %10 = mul i64 4, %9
  %11 = call noalias i8* @malloc(i64 %10)
  %12 = bitcast i8* %11 to i32*
  %13 = load %struct.Vector*, %struct.Vector** %1, align 8
  %14 = getelementptr inbounds %struct.Vector, %struct.Vector* %13, i32 0, i32 2
  store i32* %12, i32** %14, align 8
  ret void
}

; Function Attrs: nounwind
declare noalias i8* @malloc(i64)

; Function Attrs: nounwind uwtable
define void @vector_append(%struct.Vector* %vector, i32 %value) {
  %1 = alloca %struct.Vector*, align 8
  %2 = alloca i32, align 4
  store %struct.Vector* %vector, %struct.Vector** %1, align 8
  store i32 %value, i32* %2, align 4
  %3 = load %struct.Vector*, %struct.Vector** %1, align 8
  call void @vector_double_capacity_if_full(%struct.Vector* %3)
  %4 = load i32, i32* %2, align 4
  %5 = load %struct.Vector*, %struct.Vector** %1, align 8
  %6 = getelementptr inbounds %struct.Vector, %struct.Vector* %5, i32 0, i32 0
  %7 = load i32, i32* %6, align 8
  %8 = add nsw i32 %7, 1
  store i32 %8, i32* %6, align 8
  %9 = sext i32 %7 to i64
  %10 = load %struct.Vector*, %struct.Vector** %1, align 8
  %11 = getelementptr inbounds %struct.Vector, %struct.Vector* %10, i32 0, i32 2
  %12 = load i32*, i32** %11, align 8
  %13 = getelementptr inbounds i32, i32* %12, i64 %9
  store i32 %4, i32* %13, align 4
  ret void
}

; Function Attrs: nounwind uwtable
define void @vector_double_capacity_if_full(%struct.Vector* %vector) {
  %1 = alloca %struct.Vector*, align 8
  store %struct.Vector* %vector, %struct.Vector** %1, align 8
  %2 = load %struct.Vector*, %struct.Vector** %1, align 8
  %3 = getelementptr inbounds %struct.Vector, %struct.Vector* %2, i32 0, i32 0
  %4 = load i32, i32* %3, align 8
  %5 = load %struct.Vector*, %struct.Vector** %1, align 8
  %6 = getelementptr inbounds %struct.Vector, %struct.Vector* %5, i32 0, i32 1
  %7 = load i32, i32* %6, align 4
  %8 = icmp sge i32 %4, %7
  br i1 %8, label %9, label %27

; <label>:9                                       ; preds = %0
  %10 = load %struct.Vector*, %struct.Vector** %1, align 8
  %11 = getelementptr inbounds %struct.Vector, %struct.Vector* %10, i32 0, i32 1
  %12 = load i32, i32* %11, align 4
  %13 = mul nsw i32 %12, 2
  store i32 %13, i32* %11, align 4
  %14 = load %struct.Vector*, %struct.Vector** %1, align 8
  %15 = getelementptr inbounds %struct.Vector, %struct.Vector* %14, i32 0, i32 2
  %16 = load i32*, i32** %15, align 8
  %17 = bitcast i32* %16 to i8*
  %18 = load %struct.Vector*, %struct.Vector** %1, align 8
  %19 = getelementptr inbounds %struct.Vector, %struct.Vector* %18, i32 0, i32 1
  %20 = load i32, i32* %19, align 4
  %21 = sext i32 %20 to i64
  %22 = mul i64 4, %21
  %23 = call i8* @realloc(i8* %17, i64 %22)
  %24 = bitcast i8* %23 to i32*
  %25 = load %struct.Vector*, %struct.Vector** %1, align 8
  %26 = getelementptr inbounds %struct.Vector, %struct.Vector* %25, i32 0, i32 2
  store i32* %24, i32** %26, align 8
  br label %27

; <label>:27                                      ; preds = %9, %0
  ret void
}

; Function Attrs: nounwind uwtable
define i32 @vector_get(%struct.Vector* %vector, i32 %index) {
  %1 = alloca %struct.Vector*, align 8
  %2 = alloca i32, align 4
  store %struct.Vector* %vector, %struct.Vector** %1, align 8
  store i32 %index, i32* %2, align 4
  %3 = load i32, i32* %2, align 4
  %4 = load %struct.Vector*, %struct.Vector** %1, align 8
  %5 = getelementptr inbounds %struct.Vector, %struct.Vector* %4, i32 0, i32 0
  %6 = load i32, i32* %5, align 8
  %7 = icmp sge i32 %3, %6
  br i1 %7, label %11, label %8

; <label>:8                                       ; preds = %0
  %9 = load i32, i32* %2, align 4
  %10 = icmp slt i32 %9, 0
  br i1 %10, label %11, label %17

; <label>:11                                      ; preds = %8, %0
  %12 = load i32, i32* %2, align 4
  %13 = load %struct.Vector*, %struct.Vector** %1, align 8
  %14 = getelementptr inbounds %struct.Vector, %struct.Vector* %13, i32 0, i32 0
  %15 = load i32, i32* %14, align 8
  %16 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([46 x i8], [46 x i8]* @.str, i32 0, i32 0), i32 %12, i32 %15)
  call void @exit(i32 1)
  unreachable

; <label>:17                                      ; preds = %8
  %18 = load i32, i32* %2, align 4
  %19 = sext i32 %18 to i64
  %20 = load %struct.Vector*, %struct.Vector** %1, align 8
  %21 = getelementptr inbounds %struct.Vector, %struct.Vector* %20, i32 0, i32 2
  %22 = load i32*, i32** %21, align 8
  %23 = getelementptr inbounds i32, i32* %22, i64 %19
  %24 = load i32, i32* %23, align 4
  ret i32 %24
}

declare i32 @printf(i8*, ...)

; Function Attrs: noreturn nounwind
declare void @exit(i32)

; Function Attrs: nounwind uwtable
define void @vector_set(%struct.Vector* %vector, i32 %index, i32 %value) {
  %1 = alloca %struct.Vector*, align 8
  %2 = alloca i32, align 4
  %3 = alloca i32, align 4
  store %struct.Vector* %vector, %struct.Vector** %1, align 8
  store i32 %index, i32* %2, align 4
  store i32 %value, i32* %3, align 4
  br label %4

; <label>:4                                       ; preds = %10, %0
  %5 = load i32, i32* %2, align 4
  %6 = load %struct.Vector*, %struct.Vector** %1, align 8
  %7 = getelementptr inbounds %struct.Vector, %struct.Vector* %6, i32 0, i32 0
  %8 = load i32, i32* %7, align 8
  %9 = icmp sge i32 %5, %8
  br i1 %9, label %10, label %12

; <label>:10                                      ; preds = %4
  %11 = load %struct.Vector*, %struct.Vector** %1, align 8
  call void @vector_append(%struct.Vector* %11, i32 0)
  br label %4

; <label>:12                                      ; preds = %4
  %13 = load i32, i32* %3, align 4
  %14 = load i32, i32* %2, align 4
  %15 = sext i32 %14 to i64
  %16 = load %struct.Vector*, %struct.Vector** %1, align 8
  %17 = getelementptr inbounds %struct.Vector, %struct.Vector* %16, i32 0, i32 2
  %18 = load i32*, i32** %17, align 8
  %19 = getelementptr inbounds i32, i32* %18, i64 %15
  store i32 %13, i32* %19, align 4
  ret void
}

; Function Attrs: nounwind
declare i8* @realloc(i8*, i64)

; Function Attrs: nounwind uwtable
define void @vector_free(%struct.Vector* %vector) {
  %1 = alloca %struct.Vector*, align 8
  store %struct.Vector* %vector, %struct.Vector** %1, align 8
  %2 = load %struct.Vector*, %struct.Vector** %1, align 8
  %3 = getelementptr inbounds %struct.Vector, %struct.Vector* %2, i32 0, i32 2
  %4 = load i32*, i32** %3, align 8
  %5 = bitcast i32* %4 to i8*
  call void @free(i8* %5)
  ret void
}

; Function Attrs: nounwind
declare void @free(i8*)
