; ModuleID = prints

define void @"printd"(i64 %".1") {
	entry:
	  %"n" = alloca i64
	  store i64 %".1", i64* %"n"
	  %"x" = alloca i32
	  %".4" = load i64, i64* %"n"
	  %".5" = zext i32 10 to i64
	  %"divten" = udiv i64 %".4", %".5"
	  %"greaterthanzero" = icmp ugt i64 %"divten", 0
	  %".6" = load i64, i64* %"n"
	  %".7" = trunc i64 %".6" to i32
	  %"modten" = urem i32 %".7", 10
	  store i32 %"modten", i32* %"x"
	  br i1 %"greaterthanzero", label %"entry.if", label %"entry.endif"
	exit:
	  ret void
	entry.if:
	  call void @"printd"(i64 %"divten")
	  br label %"entry.endif"
	entry.endif:
	  %".12" = load i32, i32* %"x"
	  switch i32 %".12", label %"default" [i32 0, label %"case" i32 1, label %"case.1" i32 2, label %"case.2" i32 3, label %"case.3" i32 4, label %"case.4" i32 5, label %"case.5" i32 6, label %"case.6" i32 7, label %"case.7" i32 8, label %"case.8" i32 9, label %"case.9"]
	case:
	  %".14" = call i32 @"putchar"(i32 48)
	  br label %"exit"
	case.1:
	  %".16" = call i32 @"putchar"(i32 49)
	  br label %"exit"
	case.2:
	  %".18" = call i32 @"putchar"(i32 50)
	  br label %"exit"
	case.3:
	  %".20" = call i32 @"putchar"(i32 51)
	  br label %"exit"
	case.4:
	  %".22" = call i32 @"putchar"(i32 52)
	  br label %"exit"
	case.5:
	  %".24" = call i32 @"putchar"(i32 53)
	  br label %"exit"
	case.6:
	  %".26" = call i32 @"putchar"(i32 54)
	  br label %"exit"
	case.7:
	  %".28" = call i32 @"putchar"(i32 55)
	  br label %"exit"
	case.8:
	  %".30" = call i32 @"putchar"(i32 56)
	  br label %"exit"
	case.9:
	  %".32" = call i32 @"putchar"(i32 57)
	  br label %"exit"
	default:
	  br label %"exit"
}

define void @"printb"(i1 %".1") {
	entry:
	  %"equalszero" = icmp eq i1 %".1", 0
	  br i1 %"equalszero", label %"entry.if", label %"entry.else"
	exit:
	  ret void
	entry.if:
	  %".4" = call i32 @"putchar"(i32 102)
	  %".5" = call i32 @"putchar"(i32 97)
	  %".6" = call i32 @"putchar"(i32 108)
	  %".7" = call i32 @"putchar"(i32 115)
	  %".8" = call i32 @"putchar"(i32 101)
	  br label %"exit"
	entry.else:
	  %".10" = call i32 @"putchar"(i32 116)
	  %".11" = call i32 @"putchar"(i32 114)
	  %".12" = call i32 @"putchar"(i32 117)
	  %".13" = call i32 @"putchar"(i32 101)
	  br label %"exit"
	entry.endif:
	  br label %"exit"
}