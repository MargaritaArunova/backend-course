package com.backend.course.controller;

import com.backend.course.model.PostLike;
import com.backend.course.repository.PostLikeRepository;
import com.backend.course.service.LikeService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping
@RequiredArgsConstructor
public class LikeController {

    private final LikeService likeService;

    @PostMapping("/posts/{postId}/likes")
    public void likePost(@PathVariable Long postId,
                         @RequestParam("userId") Long userId) {
        likeService.likePost(postId, userId);
    }

    @DeleteMapping("/posts/{postId}/likes")
    public void unlikePost(@PathVariable Long postId,
                           @RequestParam("userId") Long userId) {
        likeService.unlikePost(postId, userId);
    }

    @GetMapping("/likes")
    public List<PostLike> getAllLikes() {
        return likeService.getAllLikes();
    }

    @GetMapping("/statistics/self-likes")
    public List<PostLikeRepository.SelfLikeStats> getSelfLikes() {
        return likeService.getSelfLikeStats();
    }
}

