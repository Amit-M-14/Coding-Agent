import collections
import math

def is_prime(x: int) -> bool:
    if x < 2:
        return False
    if x % 2 == 0:
        return x == 2
    r = int(math.isqrt(x))
    for i in range(3, r + 1, 2):
        if x % i == 0:
            return False
    return True

def minJumps(nums):
    n = len(nums)
    if n <= 1:
        return 0
    # Map from prime to list of indices where nums[idx] % prime == 0
    prime_to_indices = collections.defaultdict(list)
    for i, val in enumerate(nums):
        # factorize val to its prime divisors
        temp = val
        seen = set()
        d = 2
        while d * d <= temp:
            if temp % d == 0:
                if is_prime(d):
                    seen.add(d)
                while temp % d == 0:
                    temp //= d
            d += 1 if d == 2 else 2
        if temp > 1:
            if is_prime(temp):
                seen.add(temp)
        for p in seen:
            prime_to_indices[p].append(i)
    # BFS
    q = collections.deque([0])
    dist = [-1] * n
    dist[0] = 0
    visited_prime = set()
    while q:
        i = q.popleft()
        d = dist[i]
        # adjacent moves
        for nxt in (i - 1, i + 1):
            if 0 <= nxt < n and dist[nxt] == -1:
                dist[nxt] = d + 1
                if nxt == n - 1:
                    return dist[nxt]
                q.append(nxt)
        # prime teleport
        val = nums[i]
        # get prime factors of val
        primes = []
        temp = val
        d = 2
        while d * d <= temp:
            if temp % d == 0:
                if is_prime(d):
                    primes.append(d)
                while temp % d == 0:
                    temp //= d
            d += 1 if d == 2 else 2
        if temp > 1:
            if is_prime(temp):
                primes.append(temp)
        for p in primes:
            if p in visited_prime:
                continue
            visited_prime.add(p)
            for j in prime_to_indices[p]:
                if dist[j] == -1:
                    dist[j] = d + 1
                    if j == n - 1:
                        return dist[j]
                    q.append(j)
    return -1

# Simple test
if __name__ == "__main__":
    print(minJumps([2, 3, 5, 7, 11]))  # only adjacent moves, expect 4
    print(minJumps([4, 6, 8, 3, 9]))   # 0->1 (adjacent), 1 is 6 (prime 2,3) can jump to index 3 (3) then adjacent to 4 => 3 jumps
