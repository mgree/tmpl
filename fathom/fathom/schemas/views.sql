-- Average topic vector per person --
create view person_score
  (author_profile_id,
   topic_id,
   model_id,
   score) as
   select author_profile_id, topic_id, model_id, avg(score) from
   score natural join paper natural join author, person where
author.person_id = person.person_id group by person.author_profile_id,
model_id, topic_id;

-- Symetrized KL --
create view person_prob
   (author_profile_id,
    topic_id,
    model_id,
    prob) as
    select p1.author_profile_id, p1.topic_id, p1.model_id, p1.score/p2.total
    from person_score as p1 natural join
         (select author_profile_id, model_id, sum(score) as total from
          person_score
          group by author_profile_id, model_id) as p2;
