package com.backend.course.service;

import com.backend.course.exeption.NotFoundException;
import com.backend.course.model.Post;
import com.backend.course.model.User;
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

    public List<Post> getAll() {
        return postRepository.findAll();
    }

    public Post createPost(Long authorId, String text) {
        User author = userRepository.findById(authorId)
                .orElseThrow(() -> new NotFoundException(User.class, authorId));

        Post post = new Post();
        post.setAuthorId(authorId);
        post.setText(text);

        return postRepository.save(post);
    }

    public Post getById(Long id) {
        return postRepository.findById(id)
                .orElseThrow(() -> new NotFoundException(Post.class, id));
    }
}

