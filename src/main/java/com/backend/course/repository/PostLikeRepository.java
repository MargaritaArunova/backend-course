package com.backend.course.repository;

import com.backend.course.model.PostLike;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface PostLikeRepository extends JpaRepository<PostLike, Long> {

    Optional<PostLike> findByUserIdAndPostId(Long userId, Long postId);

    // TODO: сделать плохим, всё перенести в код для дальнейших улучшений
    @Query(value = """
            SELECT
                u.id AS user_id,
                u.nickname AS nickname,
                COUNT(l.id) AS self_likes
            FROM
                users u
            LEFT JOIN
                posts p ON u.id = p.author_id
            LEFT JOIN
                likes l ON p.id = l.post_id AND u.id = l.user_id
            GROUP BY
                u.id, u.nickname
            ORDER BY
                u.id
            """,
            nativeQuery = true)
    List<SelfLikeStats> findSelfLikeStats();

    interface SelfLikeStats {
        Long getUserId();

        String getNickname();

        Long getSelfLikes();
    }
}

