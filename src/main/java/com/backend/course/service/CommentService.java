package com.backend.course.service;

import com.backend.course.controller.exeption.UserException;
import com.backend.course.model.Comment;
import com.backend.course.model.Post;
import com.backend.course.model.User;
import com.backend.course.repository.CommentRepository;
import com.backend.course.repository.PostRepository;
import com.backend.course.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class CommentService {

    private final CommentRepository commentRepository;
    private final PostRepository postRepository;
    private final UserRepository userRepository;

    public List<Comment> getCommentsForPost(Long postId) {
        postRepository.findById(postId)
                .orElseThrow(() -> new UserException("Post with ID %s not found".formatted(postId)));

        return commentRepository.findByPostId(postId);
    }

    public Comment addComment(Long postId, Long authorId, String text) {
        Post post = postRepository.findById(postId)
                .orElseThrow(() -> new UserException("Post with ID %s not found".formatted(postId)));
        User author = userRepository.findById(authorId)
                .orElseThrow(() -> new UserException("User with ID %s not found".formatted(authorId)));

        Comment comment = new Comment();
        comment.setPostId(post.getId());
        comment.setAuthorId(author.getId());
        comment.setText(text);

        return commentRepository.save(comment);
    }
}

