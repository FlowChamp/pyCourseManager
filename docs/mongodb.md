# Mongo Structure
Each institution will have its own database. Note a '#' indicates that one should
refer to the corresponding section in this documentation.

school
    -> catalog
        -> #courses
    -> stock_charts
        -> #charts
    -> user_charts
        -> #charts

# Courses
A course within the stucture contains all of the necessary data to fully describe
it. However, it is important to note that each course must *also* contain its
department because it is already within the catalog collection.

# Charts
Charts contain only metadata regarding blocks, and then the ID of the course they
refer to
