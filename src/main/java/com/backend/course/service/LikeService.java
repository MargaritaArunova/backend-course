package com.backend.course.service;

import com.backend.course.exeption.NotFoundException;
import com.backend.course.model.Post;
import com.backend.course.model.PostLike;
import com.backend.course.model.User;
import com.backend.course.repository.PostLikeRepository;
import com.backend.course.repository.PostRepository;
import com.backend.course.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class LikeService {

    private final PostLikeRepository postLikeRepository;
    private final PostRepository postRepository;
    private final UserRepository userRepository;

    public PostLike likePost(Long postId, Long userId) {
        Post post = postRepository.findById(postId)
                .orElseThrow(() -> new NotFoundException(Post.class, postId));
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new NotFoundException(User.class, userId));

        return postLikeRepository.findByUserIdAndPostId(userId, postId)
                .orElseGet(() -> {
                    PostLike like = new PostLike();
                    like.setPostId(postId);
                    like.setUserId(userId);
                    return postLikeRepository.save(like);
                });
    }

    public void unlikePost(Long postId, Long userId) {
        postLikeRepository
                .findByUserIdAndPostId(userId, postId)
                .ifPresent(postLikeRepository::delete);
    }

    public List<PostLikeRepository.SelfLikeStats> getSelfLikeStats() {
        return postLikeRepository.findSelfLikeStats();
    }
}

