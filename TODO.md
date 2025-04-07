0. Use serialization helper in `CollectionWorker` and `CollectionResponseBuilder` (done)
1. Save / Upsert mechanism
    - Figuring out primary key from pydantic model
    - Upserting based on that primary key
    - Argument to alow duplicates (not upsert but insert)
2. Test `find_one` and `afind_one`
3. Test Filter expressions (Ensure that it's generating the correct filter query)
4. Work on sort expressions
    - Sort method should also support taking in a FieldExpression as long as it's a scalar
5. Work on field expressions
6. Work on Expressions with Nested objects
7. Work on expressions with Array objects
8. Write unit tests for expressions
9. Write unit tests for workers (document and collection)
10. Work on V1 documentation
11. Work on first release
    - set up stable branch
    - Set up repository rules
    - Set up changelog
    - Set up Pypi
    - Set up release tags
12. CI / CD
    - Deploy to pypi
    - Create release tag
    - semantic versioning
    - unit tests