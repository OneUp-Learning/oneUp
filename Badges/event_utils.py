def updateLeaderboard(course):
    from Students.models import StudentLeaderboardHistory, StudentRegisteredCourses
    from Badges.models import CourseConfigParams
    from Instructors.views.utils import utcDate
    from Badges.periodicVariables import studentScore, TimePeriods

    studentrcs = StudentRegisteredCourses.objects.filter(courseID=course)
    studentLeaders = {}
    currentTime = utcDate()

    for studentrc in studentrcs:
        # result = studentScore(studentrc.studentID, course, 0, result_only=True, gradeWarmup=True, gradeSerious=True, gradeActivity=True, gradeSkills=True)
        # xp = result['xp']
        xp = studentrc.xp
        # get all the students that have xp
        if xp > 0:
            studentLeaders[studentrc] = xp

    # Sort dict starting from most to least amount of xp. result is list of tuples
    studentLeaders = sorted(studentLeaders.items(),
                            key=lambda d: d[1], reverse=True)
    print(str(studentLeaders))

    # Get the maximum students displayed on leaderboard
    maxPositions = CourseConfigParams.objects.get(
        courseID=course).numStudentsDisplayed
    currentPosition = 1
    for student, xp in studentLeaders:
        # See if the student is currently active on the leaderboard
        studentLeaderboardData = StudentLeaderboardHistory.objects.filter(
            courseID=course, studentID=student.studentID, endTimestamp=None)
        # Assign the positions starting from the top
        if currentPosition <= maxPositions:
            if studentLeaderboardData.exists():
                oldPosition = 0
                for data in studentLeaderboardData:
                    oldPosition = data.leaderboardPosition
                # If the student has data and moved on the leaderboard, close it's previous record to preserve historic data
                if oldPosition != currentPosition:
                    studentLeaderboardData.update(endTimestamp=currentTime)

            # Create leaderboard data and give student position on the leaderboard
            studentLeaderboardRecord = StudentLeaderboardHistory()
            studentLeaderboardRecord.courseID = course
            studentLeaderboardRecord.studentID = student.studentID
            studentLeaderboardRecord.startTimestamp = currentTime
            studentLeaderboardRecord.endTimestamp = None
            studentLeaderboardRecord.leaderboardPosition = currentPosition
            studentLeaderboardRecord.save()
            currentPosition += 1
        else:
            # No need to create leaderboard record for student if the student never made the top #
            if studentLeaderboardData.exists():
                # Student has previous data on leaderboard, but it did not make the top # so end the student leaderboard run :(
                studentLeaderboardData.update(endTimestamp=currentTime)

    return
