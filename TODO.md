0. Use serialization helper in `CollectionWorker` and `CollectionResponseBuilder` (done)
1. Save / Upsert mechanism (done)
2. Test `find_one` and `afind_one` (done)
3. Singleton pattern for managing state context for driver
4. Test Filter expressions (Ensure that it's generating the correct filter query) (done)
5. Work on field expressions (done)
6. Work on Expressions with Nested objects (done)
7. Work on expressions with Array objects (done)
7. Work on special type annotations: `Union` and `Optional` (done)
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
13. Resource Benchmarking
    - Profile memory overhead
    - Profile CPU overhead
14. Future Enhancements
    - Optimized query generation from filter expressions
    - Support for _Aggregation Workers_
    - Support for _Indexed Fields_