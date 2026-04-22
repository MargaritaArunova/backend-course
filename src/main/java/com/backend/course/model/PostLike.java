package com.backend.course.model;

//import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.experimental.Accessors;

import java.time.OffsetDateTime;

//@Entity
@Getter
@Setter
@Accessors(chain = true)
@NoArgsConstructor
//@Table(name = "likes", uniqueConstraints = {
//        @UniqueConstraint(name = "uk_like_user_post", columnNames = {"user_id", "post_id"})
//})
public class PostLike {

//    @Id
//    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

//    @ManyToOne(fetch = FetchType.LAZY)
//    @JoinColumn(name = "user_id", nullable = false)
    private Long userId;

//    @ManyToOne(fetch = FetchType.LAZY)
//    @JoinColumn(name = "post_id", nullable = false)
    private Long postId;

//    @Column(name = "liked_at", nullable = false)
    private OffsetDateTime likedAt = OffsetDateTime.now();

}

