package com.backend.course.controller;

import com.backend.course.model.Post;
import com.backend.course.service.PostService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/posts")
@RequiredArgsConstructor
public class PostController {

    private final PostService postService;

    @GetMapping
    public List<Post> getAll() {
        return postService.getAll();
    }

    @GetMapping("/{id}")
    public void getPostById(@PathVariable Long id) {
        postService.getById(id);
    }

    @PostMapping
    public Post create(@RequestParam("authorId") Long authorId,
                       @RequestParam("text") String text) {
        return postService.createPost(authorId, text);
    }

    @DeleteMapping("/{id}")
    public void delete(@PathVariable Long id) {
        postService.deletePost(id);
    }
}

