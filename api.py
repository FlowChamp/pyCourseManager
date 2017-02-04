from restless.resources import Resource

courses = {
    0: {
        "prereqs": [],
        "ge_type": None ,
        "title": "Aerospace Fundamentals",
        "course_type": "Free Elective",
        "time": [
            "1",
            "Fall"
        ],
        "credits": 2.0,
        "catalog": "AERO 121"
    },
    1: {
        "prereqs": [],
        "ge_type": "D4/E",
        "title": "Healthy Living",
        "course_type": "General Ed",
        "time": [
            "1",
            "Fall"
        ],
        "credits": 4.0,
        "catalog": "KINE 250"
    }
}


class CourseResource(Resource):
    def is_authenticated(self):
        return True 
    
    def list(self):
        """GET /api/courses

        Returns:
            All courses loaded into the Manager
        """
        return courses
    
    def detail(self, cid):
        """GET /api/courses/<cid>

        Returns:
            Course <cid>, as given by the single argument
        """
        return courses[cid]

    def create(self):
        """POST /api/courses
        
        Uses self.data to create a new course 

        Returns:
            Result of creating a new course? (Need to see what Post.object.create does)
        """
        pass
    
    def update(self, cid):
        """PUT /api/posts/<cid>
        
        Returns:
            Updated course?
        """
        pass

    def delete(self, cid):
        """DELETE /api/posts/cid
        """
        pass
