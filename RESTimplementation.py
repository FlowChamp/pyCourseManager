from restless.resources import Resource

class CourseResource(Resource):
    def is_authenticated(self):
        return True 
    
    def list(self):
        """GET /api/courses

        Returns:
            All courses loaded into the Manager
        """
        return CourseManager.courses
    
    def detail(self, cid):
        """GET /api/courses/<cid>

        Returns:
            Course <cid>, as given by the single argument
        """
        return CourseManager.courses[cid]

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
