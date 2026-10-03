-- =====================================================================
-- queries.sql  |  Set C - Training Performance
-- Run AFTER setup.sql.  Dialect: SQLite.
-- Execution order: S2a -> S2b -> S2c -> S3 (D1, D2)
-- =====================================================================

-- [S2a] Average score by department (lowest first)
SELECT c.department,
       ROUND(AVG(a.score), 2) AS avg_score
FROM assessments a
JOIN courses c ON c.course_id = a.course_id
GROUP BY c.department
ORDER BY avg_score ASC, c.department ASC;

-- [S2b] Underperforming courses: average score below 60
SELECT c.course_id,
       c.course,
       ROUND(AVG(a.score), 2) AS avg_score
FROM assessments a
JOIN courses c ON c.course_id = a.course_id
GROUP BY c.course_id, c.course
HAVING AVG(a.score) < 60
ORDER BY avg_score ASC, c.course ASC;

-- [S2c] Top two batches by average score (ties broken alphabetically by batch)
SELECT batch,
       ROUND(AVG(score), 2) AS avg_score
FROM assessments
GROUP BY batch
ORDER BY AVG(score) DESC, batch ASC
LIMIT 2;

-- [S3_D1] Integrity check 1: LEFT JOIN courses -> assessments
-- Every course should have its assessments (3 each); a 0 would flag a course with no facts.
SELECT c.course_id,
       c.course,
       COUNT(a.assessment_id) AS assessment_rows
FROM courses c
LEFT JOIN assessments a ON a.course_id = c.course_id
GROUP BY c.course_id, c.course
ORDER BY c.course_id;

-- [S3_D2] Integrity check 2: fact keys with NO lookup match (expected: 0)
SELECT COUNT(*) AS unmatched_keys
FROM assessments a
LEFT JOIN courses c ON c.course_id = a.course_id
WHERE c.course_id IS NULL;
