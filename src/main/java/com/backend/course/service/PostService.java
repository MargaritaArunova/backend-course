package com.backend.course.service;

import com.backend.course.controller.exeption.UserException;
import com.backend.course.model.Post;
import com.backend.course.model.User;
import com.backend.course.repository.CommentRepository;
import com.backend.course.repository.PostLikeRepository;
import com.backend.course.repository.PostRepository;
import com.backend.course.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class PostService {

    private final PostRepository postRepository;
    private final UserRepository userRepository;
    private final CommentRepository commentRepository;
    private final PostLikeRepository postLikeRepository;

    public List<Post> getAll() {
        List<Post> posts = postRepository.findAll();
        posts.forEach(this::loadPostRelations);
        return posts;
    }

    public Post createPost(Long authorId, String text) {
        User author = userRepository.findById(authorId)
                .orElseThrow(() -> new UserException("User with ID %s not found".formatted(authorId)));

        Post post = new Post();
        post.setAuthorId(author.getId());
        post.setText(text);

        Post savedPost = postRepository.save(post);
        loadPostRelations(savedPost);
        return savedPost;
    }

    public Post getById(Long id) {
        Post post = postRepository.findById(id)
                .orElseThrow(() -> new UserException("Post with ID %s not found".formatted(id)));
        loadPostRelations(post);
        return post;
    }

    private void loadPostRelations(Post post) {
        if (post != null) {
            post.setComments(commentRepository.findByPostId(post.getId()));
            post.setLikes(postLikeRepository.findByPostId(post.getId()));
        }
    }
}

