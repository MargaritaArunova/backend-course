package com.backend.course.service;

import com.backend.course.exeption.NotFoundException;
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
        Post post = postRepository.findById(postId)
                .orElseThrow(() -> new NotFoundException(Post.class, postId));
        return commentRepository.findByPostId(post.getId());
    }

    public Comment addComment(Long postId, Long authorId, String text) {
        Post post = postRepository.findById(postId)
                .orElseThrow(() -> new NotFoundException(Post.class, postId));
        User author = userRepository.findById(authorId)
                .orElseThrow(() -> new NotFoundException(User.class, authorId));

        Comment comment = new Comment();
        comment.setPostId(postId);
        comment.setAuthorId(authorId);
        comment.setText(text);

        return commentRepository.save(comment);
    }

    public void deleteComment(Long postId, Long commentId) {
        Comment comment = commentRepository.findById(commentId)
                .orElseThrow(() -> new NotFoundException(Comment.class, commentId));

        if (!comment.getPostId().equals(postId)) {
            throw new NotFoundException(Comment.class, commentId);
        }

        commentRepository.delete(comment);
    }
}

