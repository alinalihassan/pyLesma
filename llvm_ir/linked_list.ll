; ModuleID = 'linked_list'

%struct.node = type { i32, %struct.node* }

@.str = private unnamed_addr constant [28 x i8] c"Error creating a new node.\0A\00", align 1

; Function Attrs: nounwind uwtable
define %struct.node* @create(i32 %data, %struct.node* %next) #0 {
  %1 = alloca i32, align 4
  %2 = alloca %struct.node*, align 8
  %new_node = alloca %struct.node*, align 8
  store i32 %data, i32* %1, align 4
  store %struct.node* %next, %struct.node** %2, align 8
  %3 = call noalias i8* @malloc(i64 16) #4
  %4 = bitcast i8* %3 to %struct.node*
  store %struct.node* %4, %struct.node** %new_node, align 8
  %5 = load %struct.node*, %struct.node** %new_node, align 8
  %6 = icmp eq %struct.node* %5, null
  br i1 %6, label %7, label %9

; <label>:7                                       ; preds = %0
  %8 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([28 x i8], [28 x i8]* @.str, i32 0, i32 0))
  call void @exit(i32 0) #5
  unreachable

; <label>:9                                       ; preds = %0
  %10 = load i32, i32* %1, align 4
  %11 = load %struct.node*, %struct.node** %new_node, align 8
  %12 = getelementptr inbounds %struct.node, %struct.node* %11, i32 0, i32 0
  store i32 %10, i32* %12, align 8
  %13 = load %struct.node*, %struct.node** %2, align 8
  %14 = load %struct.node*, %struct.node** %new_node, align 8
  %15 = getelementptr inbounds %struct.node, %struct.node* %14, i32 0, i32 1
  store %struct.node* %13, %struct.node** %15, align 8
  %16 = load %struct.node*, %struct.node** %new_node, align 8
  ret %struct.node* %16
}

; Function Attrs: nounwind
declare noalias i8* @malloc(i64) #1

declare i32 @printf(i8*, ...) #2

; Function Attrs: noreturn nounwind
declare void @exit(i32) #3

; Function Attrs: nounwind uwtable
define %struct.node* @prepend(%struct.node* %head, i32 %data) #0 {
  %1 = alloca %struct.node*, align 8
  %2 = alloca i32, align 4
  %new_node = alloca %struct.node*, align 8
  store %struct.node* %head, %struct.node** %1, align 8
  store i32 %data, i32* %2, align 4
  %3 = load i32, i32* %2, align 4
  %4 = load %struct.node*, %struct.node** %1, align 8
  %5 = call %struct.node* @create(i32 %3, %struct.node* %4)
  store %struct.node* %5, %struct.node** %new_node, align 8
  %6 = load %struct.node*, %struct.node** %new_node, align 8
  store %struct.node* %6, %struct.node** %1, align 8
  %7 = load %struct.node*, %struct.node** %1, align 8
  ret %struct.node* %7
}

; Function Attrs: nounwind uwtable
define %struct.node* @append(%struct.node* %head, i32 %data) #0 {
  %1 = alloca %struct.node*, align 8
  %2 = alloca %struct.node*, align 8
  %3 = alloca i32, align 4
  %cursor = alloca %struct.node*, align 8
  %new_node = alloca %struct.node*, align 8
  store %struct.node* %head, %struct.node** %2, align 8
  store i32 %data, i32* %3, align 4
  %4 = load %struct.node*, %struct.node** %2, align 8
  %5 = icmp eq %struct.node* %4, null
  br i1 %5, label %6, label %7

; <label>:6                                       ; preds = %0
  store %struct.node* null, %struct.node** %1, align 8
  br label %25

; <label>:7                                       ; preds = %0
  %8 = load %struct.node*, %struct.node** %2, align 8
  store %struct.node* %8, %struct.node** %cursor, align 8
  br label %9

; <label>:9                                       ; preds = %14, %7
  %10 = load %struct.node*, %struct.node** %cursor, align 8
  %11 = getelementptr inbounds %struct.node, %struct.node* %10, i32 0, i32 1
  %12 = load %struct.node*, %struct.node** %11, align 8
  %13 = icmp ne %struct.node* %12, null
  br i1 %13, label %14, label %18

; <label>:14                                      ; preds = %9
  %15 = load %struct.node*, %struct.node** %cursor, align 8
  %16 = getelementptr inbounds %struct.node, %struct.node* %15, i32 0, i32 1
  %17 = load %struct.node*, %struct.node** %16, align 8
  store %struct.node* %17, %struct.node** %cursor, align 8
  br label %9

; <label>:18                                      ; preds = %9
  %19 = load i32, i32* %3, align 4
  %20 = call %struct.node* @create(i32 %19, %struct.node* null)
  store %struct.node* %20, %struct.node** %new_node, align 8
  %21 = load %struct.node*, %struct.node** %new_node, align 8
  %22 = load %struct.node*, %struct.node** %cursor, align 8
  %23 = getelementptr inbounds %struct.node, %struct.node* %22, i32 0, i32 1
  store %struct.node* %21, %struct.node** %23, align 8
  %24 = load %struct.node*, %struct.node** %2, align 8
  store %struct.node* %24, %struct.node** %1, align 8
  br label %25

; <label>:25                                      ; preds = %18, %6
  %26 = load %struct.node*, %struct.node** %1, align 8
  ret %struct.node* %26
}

; Function Attrs: nounwind uwtable
define %struct.node* @insert_after(%struct.node* %head, i32 %data, %struct.node* %prev) #0 {
  %1 = alloca %struct.node*, align 8
  %2 = alloca %struct.node*, align 8
  %3 = alloca i32, align 4
  %4 = alloca %struct.node*, align 8
  %cursor = alloca %struct.node*, align 8
  %new_node = alloca %struct.node*, align 8
  store %struct.node* %head, %struct.node** %2, align 8
  store i32 %data, i32* %3, align 4
  store %struct.node* %prev, %struct.node** %4, align 8
  %5 = load %struct.node*, %struct.node** %2, align 8
  %6 = icmp eq %struct.node* %5, null
  br i1 %6, label %10, label %7

; <label>:7                                       ; preds = %0
  %8 = load %struct.node*, %struct.node** %4, align 8
  %9 = icmp eq %struct.node* %8, null
  br i1 %9, label %10, label %11

; <label>:10                                      ; preds = %7, %0
  store %struct.node* null, %struct.node** %1, align 8
  br label %35

; <label>:11                                      ; preds = %7
  %12 = load %struct.node*, %struct.node** %2, align 8
  store %struct.node* %12, %struct.node** %cursor, align 8
  br label %13

; <label>:13                                      ; preds = %17, %11
  %14 = load %struct.node*, %struct.node** %cursor, align 8
  %15 = load %struct.node*, %struct.node** %4, align 8
  %16 = icmp ne %struct.node* %14, %15
  br i1 %16, label %17, label %21

; <label>:17                                      ; preds = %13
  %18 = load %struct.node*, %struct.node** %cursor, align 8
  %19 = getelementptr inbounds %struct.node, %struct.node* %18, i32 0, i32 1
  %20 = load %struct.node*, %struct.node** %19, align 8
  store %struct.node* %20, %struct.node** %cursor, align 8
  br label %13

; <label>:21                                      ; preds = %13
  %22 = load %struct.node*, %struct.node** %cursor, align 8
  %23 = icmp ne %struct.node* %22, null
  br i1 %23, label %24, label %34

; <label>:24                                      ; preds = %21
  %25 = load i32, i32* %3, align 4
  %26 = load %struct.node*, %struct.node** %cursor, align 8
  %27 = getelementptr inbounds %struct.node, %struct.node* %26, i32 0, i32 1
  %28 = load %struct.node*, %struct.node** %27, align 8
  %29 = call %struct.node* @create(i32 %25, %struct.node* %28)
  store %struct.node* %29, %struct.node** %new_node, align 8
  %30 = load %struct.node*, %struct.node** %new_node, align 8
  %31 = load %struct.node*, %struct.node** %cursor, align 8
  %32 = getelementptr inbounds %struct.node, %struct.node* %31, i32 0, i32 1
  store %struct.node* %30, %struct.node** %32, align 8
  %33 = load %struct.node*, %struct.node** %2, align 8
  store %struct.node* %33, %struct.node** %1, align 8
  br label %35

; <label>:34                                      ; preds = %21
  store %struct.node* null, %struct.node** %1, align 8
  br label %35

; <label>:35                                      ; preds = %34, %24, %10
  %36 = load %struct.node*, %struct.node** %1, align 8
  ret %struct.node* %36
}

; Function Attrs: nounwind uwtable
define %struct.node* @insert_before(%struct.node* %head, i32 %data, %struct.node* %nxt) #0 {
  %1 = alloca %struct.node*, align 8
  %2 = alloca %struct.node*, align 8
  %3 = alloca i32, align 4
  %4 = alloca %struct.node*, align 8
  %cursor = alloca %struct.node*, align 8
  %new_node = alloca %struct.node*, align 8
  store %struct.node* %head, %struct.node** %2, align 8
  store i32 %data, i32* %3, align 4
  store %struct.node* %nxt, %struct.node** %4, align 8
  %5 = load %struct.node*, %struct.node** %4, align 8
  %6 = icmp eq %struct.node* %5, null
  br i1 %6, label %10, label %7

; <label>:7                                       ; preds = %0
  %8 = load %struct.node*, %struct.node** %2, align 8
  %9 = icmp eq %struct.node* %8, null
  br i1 %9, label %10, label %11

; <label>:10                                      ; preds = %7, %0
  store %struct.node* null, %struct.node** %1, align 8
  br label %50

; <label>:11                                      ; preds = %7
  %12 = load %struct.node*, %struct.node** %2, align 8
  %13 = load %struct.node*, %struct.node** %4, align 8
  %14 = icmp eq %struct.node* %12, %13
  br i1 %14, label %15, label %20

; <label>:15                                      ; preds = %11
  %16 = load %struct.node*, %struct.node** %2, align 8
  %17 = load i32, i32* %3, align 4
  %18 = call %struct.node* @prepend(%struct.node* %16, i32 %17)
  store %struct.node* %18, %struct.node** %2, align 8
  %19 = load %struct.node*, %struct.node** %2, align 8
  store %struct.node* %19, %struct.node** %1, align 8
  br label %50

; <label>:20                                      ; preds = %11
  %21 = load %struct.node*, %struct.node** %2, align 8
  store %struct.node* %21, %struct.node** %cursor, align 8
  br label %22

; <label>:22                                      ; preds = %32, %20
  %23 = load %struct.node*, %struct.node** %cursor, align 8
  %24 = icmp ne %struct.node* %23, null
  br i1 %24, label %25, label %36

; <label>:25                                      ; preds = %22
  %26 = load %struct.node*, %struct.node** %cursor, align 8
  %27 = getelementptr inbounds %struct.node, %struct.node* %26, i32 0, i32 1
  %28 = load %struct.node*, %struct.node** %27, align 8
  %29 = load %struct.node*, %struct.node** %4, align 8
  %30 = icmp eq %struct.node* %28, %29
  br i1 %30, label %31, label %32

; <label>:31                                      ; preds = %25
  br label %36

; <label>:32                                      ; preds = %25
  %33 = load %struct.node*, %struct.node** %cursor, align 8
  %34 = getelementptr inbounds %struct.node, %struct.node* %33, i32 0, i32 1
  %35 = load %struct.node*, %struct.node** %34, align 8
  store %struct.node* %35, %struct.node** %cursor, align 8
  br label %22

; <label>:36                                      ; preds = %31, %22
  %37 = load %struct.node*, %struct.node** %cursor, align 8
  %38 = icmp ne %struct.node* %37, null
  br i1 %38, label %39, label %49

; <label>:39                                      ; preds = %36
  %40 = load i32, i32* %3, align 4
  %41 = load %struct.node*, %struct.node** %cursor, align 8
  %42 = getelementptr inbounds %struct.node, %struct.node* %41, i32 0, i32 1
  %43 = load %struct.node*, %struct.node** %42, align 8
  %44 = call %struct.node* @create(i32 %40, %struct.node* %43)
  store %struct.node* %44, %struct.node** %new_node, align 8
  %45 = load %struct.node*, %struct.node** %new_node, align 8
  %46 = load %struct.node*, %struct.node** %cursor, align 8
  %47 = getelementptr inbounds %struct.node, %struct.node* %46, i32 0, i32 1
  store %struct.node* %45, %struct.node** %47, align 8
  %48 = load %struct.node*, %struct.node** %2, align 8
  store %struct.node* %48, %struct.node** %1, align 8
  br label %50

; <label>:49                                      ; preds = %36
  store %struct.node* null, %struct.node** %1, align 8
  br label %50

; <label>:50                                      ; preds = %49, %39, %15, %10
  %51 = load %struct.node*, %struct.node** %1, align 8
  ret %struct.node* %51
}

; Function Attrs: nounwind uwtable
define void @traverse(%struct.node* %head, void (%struct.node*)* %f) #0 {
  %1 = alloca %struct.node*, align 8
  %2 = alloca void (%struct.node*)*, align 8
  %cursor = alloca %struct.node*, align 8
  store %struct.node* %head, %struct.node** %1, align 8
  store void (%struct.node*)* %f, void (%struct.node*)** %2, align 8
  %3 = load %struct.node*, %struct.node** %1, align 8
  store %struct.node* %3, %struct.node** %cursor, align 8
  br label %4

; <label>:4                                       ; preds = %7, %0
  %5 = load %struct.node*, %struct.node** %cursor, align 8
  %6 = icmp ne %struct.node* %5, null
  br i1 %6, label %7, label %13

; <label>:7                                       ; preds = %4
  %8 = load void (%struct.node*)*, void (%struct.node*)** %2, align 8
  %9 = load %struct.node*, %struct.node** %cursor, align 8
  call void %8(%struct.node* %9)
  %10 = load %struct.node*, %struct.node** %cursor, align 8
  %11 = getelementptr inbounds %struct.node, %struct.node* %10, i32 0, i32 1
  %12 = load %struct.node*, %struct.node** %11, align 8
  store %struct.node* %12, %struct.node** %cursor, align 8
  br label %4

; <label>:13                                      ; preds = %4
  ret void
}

; Function Attrs: nounwind uwtable
define %struct.node* @remove_front(%struct.node* %head) #0 {
  %1 = alloca %struct.node*, align 8
  %2 = alloca %struct.node*, align 8
  %front = alloca %struct.node*, align 8
  store %struct.node* %head, %struct.node** %2, align 8
  %3 = load %struct.node*, %struct.node** %2, align 8
  %4 = icmp eq %struct.node* %3, null
  br i1 %4, label %5, label %6

; <label>:5                                       ; preds = %0
  store %struct.node* null, %struct.node** %1, align 8
  br label %21

; <label>:6                                       ; preds = %0
  %7 = load %struct.node*, %struct.node** %2, align 8
  store %struct.node* %7, %struct.node** %front, align 8
  %8 = load %struct.node*, %struct.node** %2, align 8
  %9 = getelementptr inbounds %struct.node, %struct.node* %8, i32 0, i32 1
  %10 = load %struct.node*, %struct.node** %9, align 8
  store %struct.node* %10, %struct.node** %2, align 8
  %11 = load %struct.node*, %struct.node** %front, align 8
  %12 = getelementptr inbounds %struct.node, %struct.node* %11, i32 0, i32 1
  store %struct.node* null, %struct.node** %12, align 8
  %13 = load %struct.node*, %struct.node** %front, align 8
  %14 = load %struct.node*, %struct.node** %2, align 8
  %15 = icmp eq %struct.node* %13, %14
  br i1 %15, label %16, label %17

; <label>:16                                      ; preds = %6
  store %struct.node* null, %struct.node** %2, align 8
  br label %17

; <label>:17                                      ; preds = %16, %6
  %18 = load %struct.node*, %struct.node** %front, align 8
  %19 = bitcast %struct.node* %18 to i8*
  call void @free(i8* %19) #4
  %20 = load %struct.node*, %struct.node** %2, align 8
  store %struct.node* %20, %struct.node** %1, align 8
  br label %21

; <label>:21                                      ; preds = %17, %5
  %22 = load %struct.node*, %struct.node** %1, align 8
  ret %struct.node* %22
}

; Function Attrs: nounwind
declare void @free(i8*) #1

; Function Attrs: nounwind uwtable
define %struct.node* @remove_back(%struct.node* %head) #0 {
  %1 = alloca %struct.node*, align 8
  %2 = alloca %struct.node*, align 8
  %cursor = alloca %struct.node*, align 8
  %back = alloca %struct.node*, align 8
  store %struct.node* %head, %struct.node** %2, align 8
  %3 = load %struct.node*, %struct.node** %2, align 8
  %4 = icmp eq %struct.node* %3, null
  br i1 %4, label %5, label %6

; <label>:5                                       ; preds = %0
  store %struct.node* null, %struct.node** %1, align 8
  br label %33

; <label>:6                                       ; preds = %0
  %7 = load %struct.node*, %struct.node** %2, align 8
  store %struct.node* %7, %struct.node** %cursor, align 8
  store %struct.node* null, %struct.node** %back, align 8
  br label %8

; <label>:8                                       ; preds = %13, %6
  %9 = load %struct.node*, %struct.node** %cursor, align 8
  %10 = getelementptr inbounds %struct.node, %struct.node* %9, i32 0, i32 1
  %11 = load %struct.node*, %struct.node** %10, align 8
  %12 = icmp ne %struct.node* %11, null
  br i1 %12, label %13, label %18

; <label>:13                                      ; preds = %8
  %14 = load %struct.node*, %struct.node** %cursor, align 8
  store %struct.node* %14, %struct.node** %back, align 8
  %15 = load %struct.node*, %struct.node** %cursor, align 8
  %16 = getelementptr inbounds %struct.node, %struct.node* %15, i32 0, i32 1
  %17 = load %struct.node*, %struct.node** %16, align 8
  store %struct.node* %17, %struct.node** %cursor, align 8
  br label %8

; <label>:18                                      ; preds = %8
  %19 = load %struct.node*, %struct.node** %back, align 8
  %20 = icmp ne %struct.node* %19, null
  br i1 %20, label %21, label %24

; <label>:21                                      ; preds = %18
  %22 = load %struct.node*, %struct.node** %back, align 8
  %23 = getelementptr inbounds %struct.node, %struct.node* %22, i32 0, i32 1
  store %struct.node* null, %struct.node** %23, align 8
  br label %24

; <label>:24                                      ; preds = %21, %18
  %25 = load %struct.node*, %struct.node** %cursor, align 8
  %26 = load %struct.node*, %struct.node** %2, align 8
  %27 = icmp eq %struct.node* %25, %26
  br i1 %27, label %28, label %29

; <label>:28                                      ; preds = %24
  store %struct.node* null, %struct.node** %2, align 8
  br label %29

; <label>:29                                      ; preds = %28, %24
  %30 = load %struct.node*, %struct.node** %cursor, align 8
  %31 = bitcast %struct.node* %30 to i8*
  call void @free(i8* %31) #4
  %32 = load %struct.node*, %struct.node** %2, align 8
  store %struct.node* %32, %struct.node** %1, align 8
  br label %33

; <label>:33                                      ; preds = %29, %5
  %34 = load %struct.node*, %struct.node** %1, align 8
  ret %struct.node* %34
}

; Function Attrs: nounwind uwtable
define %struct.node* @remove_any(%struct.node* %head, %struct.node* %nd) #0 {
  %1 = alloca %struct.node*, align 8
  %2 = alloca %struct.node*, align 8
  %3 = alloca %struct.node*, align 8
  %cursor = alloca %struct.node*, align 8
  %tmp = alloca %struct.node*, align 8
  store %struct.node* %head, %struct.node** %2, align 8
  store %struct.node* %nd, %struct.node** %3, align 8
  %4 = load %struct.node*, %struct.node** %3, align 8
  %5 = icmp eq %struct.node* %4, null
  br i1 %5, label %6, label %7

; <label>:6                                       ; preds = %0
  store %struct.node* null, %struct.node** %1, align 8
  br label %56

; <label>:7                                       ; preds = %0
  %8 = load %struct.node*, %struct.node** %3, align 8
  %9 = load %struct.node*, %struct.node** %2, align 8
  %10 = icmp eq %struct.node* %8, %9
  br i1 %10, label %11, label %14

; <label>:11                                      ; preds = %7
  %12 = load %struct.node*, %struct.node** %2, align 8
  %13 = call %struct.node* @remove_front(%struct.node* %12)
  store %struct.node* %13, %struct.node** %1, align 8
  br label %56

; <label>:14                                      ; preds = %7
  %15 = load %struct.node*, %struct.node** %3, align 8
  %16 = getelementptr inbounds %struct.node, %struct.node* %15, i32 0, i32 1
  %17 = load %struct.node*, %struct.node** %16, align 8
  %18 = icmp eq %struct.node* %17, null
  br i1 %18, label %19, label %22

; <label>:19                                      ; preds = %14
  %20 = load %struct.node*, %struct.node** %2, align 8
  %21 = call %struct.node* @remove_back(%struct.node* %20)
  store %struct.node* %21, %struct.node** %1, align 8
  br label %56

; <label>:22                                      ; preds = %14
  %23 = load %struct.node*, %struct.node** %2, align 8
  store %struct.node* %23, %struct.node** %cursor, align 8
  br label %24

; <label>:24                                      ; preds = %34, %22
  %25 = load %struct.node*, %struct.node** %cursor, align 8
  %26 = icmp ne %struct.node* %25, null
  br i1 %26, label %27, label %38

; <label>:27                                      ; preds = %24
  %28 = load %struct.node*, %struct.node** %cursor, align 8
  %29 = getelementptr inbounds %struct.node, %struct.node* %28, i32 0, i32 1
  %30 = load %struct.node*, %struct.node** %29, align 8
  %31 = load %struct.node*, %struct.node** %3, align 8
  %32 = icmp eq %struct.node* %30, %31
  br i1 %32, label %33, label %34

; <label>:33                                      ; preds = %27
  br label %38

; <label>:34                                      ; preds = %27
  %35 = load %struct.node*, %struct.node** %cursor, align 8
  %36 = getelementptr inbounds %struct.node, %struct.node* %35, i32 0, i32 1
  %37 = load %struct.node*, %struct.node** %36, align 8
  store %struct.node* %37, %struct.node** %cursor, align 8
  br label %24

; <label>:38                                      ; preds = %33, %24
  %39 = load %struct.node*, %struct.node** %cursor, align 8
  %40 = icmp ne %struct.node* %39, null
  br i1 %40, label %41, label %54

; <label>:41                                      ; preds = %38
  %42 = load %struct.node*, %struct.node** %cursor, align 8
  %43 = getelementptr inbounds %struct.node, %struct.node* %42, i32 0, i32 1
  %44 = load %struct.node*, %struct.node** %43, align 8
  store %struct.node* %44, %struct.node** %tmp, align 8
  %45 = load %struct.node*, %struct.node** %tmp, align 8
  %46 = getelementptr inbounds %struct.node, %struct.node* %45, i32 0, i32 1
  %47 = load %struct.node*, %struct.node** %46, align 8
  %48 = load %struct.node*, %struct.node** %cursor, align 8
  %49 = getelementptr inbounds %struct.node, %struct.node* %48, i32 0, i32 1
  store %struct.node* %47, %struct.node** %49, align 8
  %50 = load %struct.node*, %struct.node** %tmp, align 8
  %51 = getelementptr inbounds %struct.node, %struct.node* %50, i32 0, i32 1
  store %struct.node* null, %struct.node** %51, align 8
  %52 = load %struct.node*, %struct.node** %tmp, align 8
  %53 = bitcast %struct.node* %52 to i8*
  call void @free(i8* %53) #4
  br label %54

; <label>:54                                      ; preds = %41, %38
  %55 = load %struct.node*, %struct.node** %2, align 8
  store %struct.node* %55, %struct.node** %1, align 8
  br label %56

; <label>:56                                      ; preds = %54, %19, %11, %6
  %57 = load %struct.node*, %struct.node** %1, align 8
  ret %struct.node* %57
}

; Function Attrs: nounwind uwtable
define %struct.node* @search(%struct.node* %head, i32 %data) #0 {
  %1 = alloca %struct.node*, align 8
  %2 = alloca %struct.node*, align 8
  %3 = alloca i32, align 4
  %cursor = alloca %struct.node*, align 8
  store %struct.node* %head, %struct.node** %2, align 8
  store i32 %data, i32* %3, align 4
  %4 = load %struct.node*, %struct.node** %2, align 8
  store %struct.node* %4, %struct.node** %cursor, align 8
  br label %5

; <label>:5                                       ; preds = %16, %0
  %6 = load %struct.node*, %struct.node** %cursor, align 8
  %7 = icmp ne %struct.node* %6, null
  br i1 %7, label %8, label %20

; <label>:8                                       ; preds = %5
  %9 = load %struct.node*, %struct.node** %cursor, align 8
  %10 = getelementptr inbounds %struct.node, %struct.node* %9, i32 0, i32 0
  %11 = load i32, i32* %10, align 8
  %12 = load i32, i32* %3, align 4
  %13 = icmp eq i32 %11, %12
  br i1 %13, label %14, label %16

; <label>:14                                      ; preds = %8
  %15 = load %struct.node*, %struct.node** %cursor, align 8
  store %struct.node* %15, %struct.node** %1, align 8
  br label %21

; <label>:16                                      ; preds = %8
  %17 = load %struct.node*, %struct.node** %cursor, align 8
  %18 = getelementptr inbounds %struct.node, %struct.node* %17, i32 0, i32 1
  %19 = load %struct.node*, %struct.node** %18, align 8
  store %struct.node* %19, %struct.node** %cursor, align 8
  br label %5

; <label>:20                                      ; preds = %5
  store %struct.node* null, %struct.node** %1, align 8
  br label %21

; <label>:21                                      ; preds = %20, %14
  %22 = load %struct.node*, %struct.node** %1, align 8
  ret %struct.node* %22
}

; Function Attrs: nounwind uwtable
define void @dispose(%struct.node* %head) #0 {
  %1 = alloca %struct.node*, align 8
  %cursor = alloca %struct.node*, align 8
  %tmp = alloca %struct.node*, align 8
  store %struct.node* %head, %struct.node** %1, align 8
  %2 = load %struct.node*, %struct.node** %1, align 8
  %3 = icmp ne %struct.node* %2, null
  br i1 %3, label %4, label %21

; <label>:4                                       ; preds = %0
  %5 = load %struct.node*, %struct.node** %1, align 8
  %6 = getelementptr inbounds %struct.node, %struct.node* %5, i32 0, i32 1
  %7 = load %struct.node*, %struct.node** %6, align 8
  store %struct.node* %7, %struct.node** %cursor, align 8
  %8 = load %struct.node*, %struct.node** %1, align 8
  %9 = getelementptr inbounds %struct.node, %struct.node* %8, i32 0, i32 1
  store %struct.node* null, %struct.node** %9, align 8
  br label %10

; <label>:10                                      ; preds = %13, %4
  %11 = load %struct.node*, %struct.node** %cursor, align 8
  %12 = icmp ne %struct.node* %11, null
  br i1 %12, label %13, label %20

; <label>:13                                      ; preds = %10
  %14 = load %struct.node*, %struct.node** %cursor, align 8
  %15 = getelementptr inbounds %struct.node, %struct.node* %14, i32 0, i32 1
  %16 = load %struct.node*, %struct.node** %15, align 8
  store %struct.node* %16, %struct.node** %tmp, align 8
  %17 = load %struct.node*, %struct.node** %cursor, align 8
  %18 = bitcast %struct.node* %17 to i8*
  call void @free(i8* %18) #4
  %19 = load %struct.node*, %struct.node** %tmp, align 8
  store %struct.node* %19, %struct.node** %cursor, align 8
  br label %10

; <label>:20                                      ; preds = %10
  br label %21

; <label>:21                                      ; preds = %20, %0
  ret void
}

; Function Attrs: nounwind uwtable
define i32 @count(%struct.node* %head) #0 {
  %1 = alloca %struct.node*, align 8
  %cursor = alloca %struct.node*, align 8
  %c = alloca i32, align 4
  store %struct.node* %head, %struct.node** %1, align 8
  %2 = load %struct.node*, %struct.node** %1, align 8
  store %struct.node* %2, %struct.node** %cursor, align 8
  store i32 0, i32* %c, align 4
  br label %3

; <label>:3                                       ; preds = %6, %0
  %4 = load %struct.node*, %struct.node** %cursor, align 8
  %5 = icmp ne %struct.node* %4, null
  br i1 %5, label %6, label %12

; <label>:6                                       ; preds = %3
  %7 = load i32, i32* %c, align 4
  %8 = add nsw i32 %7, 1
  store i32 %8, i32* %c, align 4
  %9 = load %struct.node*, %struct.node** %cursor, align 8
  %10 = getelementptr inbounds %struct.node, %struct.node* %9, i32 0, i32 1
  %11 = load %struct.node*, %struct.node** %10, align 8
  store %struct.node* %11, %struct.node** %cursor, align 8
  br label %3

; <label>:12                                      ; preds = %3
  %13 = load i32, i32* %c, align 4
  ret i32 %13
}

; Function Attrs: nounwind uwtable
define %struct.node* @insertion_sort(%struct.node* %head) #0 {
  %1 = alloca %struct.node*, align 8
  %x = alloca %struct.node*, align 8
  %y = alloca %struct.node*, align 8
  %e = alloca %struct.node*, align 8
  store %struct.node* %head, %struct.node** %1, align 8
  %2 = load %struct.node*, %struct.node** %1, align 8
  store %struct.node* %2, %struct.node** %x, align 8
  store %struct.node* null, %struct.node** %1, align 8
  br label %3

; <label>:3                                       ; preds = %63, %0
  %4 = load %struct.node*, %struct.node** %x, align 8
  %5 = icmp ne %struct.node* %4, null
  br i1 %5, label %6, label %64

; <label>:6                                       ; preds = %3
  %7 = load %struct.node*, %struct.node** %x, align 8
  store %struct.node* %7, %struct.node** %e, align 8
  %8 = load %struct.node*, %struct.node** %x, align 8
  %9 = getelementptr inbounds %struct.node, %struct.node* %8, i32 0, i32 1
  %10 = load %struct.node*, %struct.node** %9, align 8
  store %struct.node* %10, %struct.node** %x, align 8
  %11 = load %struct.node*, %struct.node** %1, align 8
  %12 = icmp ne %struct.node* %11, null
  br i1 %12, label %13, label %59

; <label>:13                                      ; preds = %6
  %14 = load %struct.node*, %struct.node** %e, align 8
  %15 = getelementptr inbounds %struct.node, %struct.node* %14, i32 0, i32 0
  %16 = load i32, i32* %15, align 8
  %17 = load %struct.node*, %struct.node** %1, align 8
  %18 = getelementptr inbounds %struct.node, %struct.node* %17, i32 0, i32 0
  %19 = load i32, i32* %18, align 8
  %20 = icmp sgt i32 %16, %19
  br i1 %20, label %21, label %53

; <label>:21                                      ; preds = %13
  %22 = load %struct.node*, %struct.node** %1, align 8
  store %struct.node* %22, %struct.node** %y, align 8
  br label %23

; <label>:23                                      ; preds = %40, %21
  %24 = load %struct.node*, %struct.node** %y, align 8
  %25 = getelementptr inbounds %struct.node, %struct.node* %24, i32 0, i32 1
  %26 = load %struct.node*, %struct.node** %25, align 8
  %27 = icmp ne %struct.node* %26, null
  br i1 %27, label %28, label %38

; <label>:28                                      ; preds = %23
  %29 = load %struct.node*, %struct.node** %e, align 8
  %30 = getelementptr inbounds %struct.node, %struct.node* %29, i32 0, i32 0
  %31 = load i32, i32* %30, align 8
  %32 = load %struct.node*, %struct.node** %y, align 8
  %33 = getelementptr inbounds %struct.node, %struct.node* %32, i32 0, i32 1
  %34 = load %struct.node*, %struct.node** %33, align 8
  %35 = getelementptr inbounds %struct.node, %struct.node* %34, i32 0, i32 0
  %36 = load i32, i32* %35, align 8
  %37 = icmp sgt i32 %31, %36
  br label %38

; <label>:38                                      ; preds = %28, %23
  %39 = phi i1 [ false, %23 ], [ %37, %28 ]
  br i1 %39, label %40, label %44

; <label>:40                                      ; preds = %38
  %41 = load %struct.node*, %struct.node** %y, align 8
  %42 = getelementptr inbounds %struct.node, %struct.node* %41, i32 0, i32 1
  %43 = load %struct.node*, %struct.node** %42, align 8
  store %struct.node* %43, %struct.node** %y, align 8
  br label %23

; <label>:44                                      ; preds = %38
  %45 = load %struct.node*, %struct.node** %y, align 8
  %46 = getelementptr inbounds %struct.node, %struct.node* %45, i32 0, i32 1
  %47 = load %struct.node*, %struct.node** %46, align 8
  %48 = load %struct.node*, %struct.node** %e, align 8
  %49 = getelementptr inbounds %struct.node, %struct.node* %48, i32 0, i32 1
  store %struct.node* %47, %struct.node** %49, align 8
  %50 = load %struct.node*, %struct.node** %e, align 8
  %51 = load %struct.node*, %struct.node** %y, align 8
  %52 = getelementptr inbounds %struct.node, %struct.node* %51, i32 0, i32 1
  store %struct.node* %50, %struct.node** %52, align 8
  br label %58

; <label>:53                                      ; preds = %13
  %54 = load %struct.node*, %struct.node** %1, align 8
  %55 = load %struct.node*, %struct.node** %e, align 8
  %56 = getelementptr inbounds %struct.node, %struct.node* %55, i32 0, i32 1
  store %struct.node* %54, %struct.node** %56, align 8
  %57 = load %struct.node*, %struct.node** %e, align 8
  store %struct.node* %57, %struct.node** %1, align 8
  br label %58

; <label>:58                                      ; preds = %53, %44
  br label %63

; <label>:59                                      ; preds = %6
  %60 = load %struct.node*, %struct.node** %e, align 8
  %61 = getelementptr inbounds %struct.node, %struct.node* %60, i32 0, i32 1
  store %struct.node* null, %struct.node** %61, align 8
  %62 = load %struct.node*, %struct.node** %e, align 8
  store %struct.node* %62, %struct.node** %1, align 8
  br label %63

; <label>:63                                      ; preds = %59, %58
  br label %3

; <label>:64                                      ; preds = %3
  %65 = load %struct.node*, %struct.node** %1, align 8
  ret %struct.node* %65
}

; Function Attrs: nounwind uwtable
define %struct.node* @reverse(%struct.node* %head) #0 {
  %1 = alloca %struct.node*, align 8
  %prev = alloca %struct.node*, align 8
  %current = alloca %struct.node*, align 8
  %next = alloca %struct.node*, align 8
  store %struct.node* %head, %struct.node** %1, align 8
  store %struct.node* null, %struct.node** %prev, align 8
  %2 = load %struct.node*, %struct.node** %1, align 8
  store %struct.node* %2, %struct.node** %current, align 8
  br label %3

; <label>:3                                       ; preds = %6, %0
  %4 = load %struct.node*, %struct.node** %current, align 8
  %5 = icmp ne %struct.node* %4, null
  br i1 %5, label %6, label %15

; <label>:6                                       ; preds = %3
  %7 = load %struct.node*, %struct.node** %current, align 8
  %8 = getelementptr inbounds %struct.node, %struct.node* %7, i32 0, i32 1
  %9 = load %struct.node*, %struct.node** %8, align 8
  store %struct.node* %9, %struct.node** %next, align 8
  %10 = load %struct.node*, %struct.node** %prev, align 8
  %11 = load %struct.node*, %struct.node** %current, align 8
  %12 = getelementptr inbounds %struct.node, %struct.node* %11, i32 0, i32 1
  store %struct.node* %10, %struct.node** %12, align 8
  %13 = load %struct.node*, %struct.node** %current, align 8
  store %struct.node* %13, %struct.node** %prev, align 8
  %14 = load %struct.node*, %struct.node** %next, align 8
  store %struct.node* %14, %struct.node** %current, align 8
  br label %3

; <label>:15                                      ; preds = %3
  %16 = load %struct.node*, %struct.node** %prev, align 8
  store %struct.node* %16, %struct.node** %1, align 8
  %17 = load %struct.node*, %struct.node** %1, align 8
  ret %struct.node* %17
}

attributes #0 = { nounwind uwtable "disable-tail-calls"="false" "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+fxsr,+mmx,+sse,+sse2" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #1 = { nounwind "disable-tail-calls"="false" "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+fxsr,+mmx,+sse,+sse2" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #2 = { "disable-tail-calls"="false" "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+fxsr,+mmx,+sse,+sse2" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #3 = { noreturn nounwind "disable-tail-calls"="false" "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+fxsr,+mmx,+sse,+sse2" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #4 = { nounwind }
attributes #5 = { noreturn nounwind }

!llvm.ident = !{!0}

!0 = !{!"clang version 3.8.0-2ubuntu4 (tags/RELEASE_380/final)"}
