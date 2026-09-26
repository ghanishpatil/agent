1160:	endbr64	
1164:	xor	ebp, ebp
1166:	mov	r9, rdx
1169:	pop	rsi
116a:	mov	rdx, rsp
116d:	and	rsp, 0xfffffffffffffff0
1171:	push	rax
1172:	push	rsp
1173:	xor	r8d, r8d
1176:	xor	ecx, ecx
1178:	lea	rdi, [rip + 0x856]
117f:	call	qword ptr [rip + 0x2e4b]
1185:	hlt	
1186:	nop	word ptr cs:[rax + rax]
1190:	lea	rdi, [rip + 0x2e79]
1197:	lea	rax, [rip + 0x2e72]
119e:	cmp	rax, rdi
11a1:	je	0x11b8
11a3:	mov	rax, qword ptr [rip + 0x2e2e]
11aa:	test	rax, rax
11ad:	je	0x11b8
11af:	jmp	rax
11b1:	nop	dword ptr [rax]
11b8:	ret	
11b9:	nop	dword ptr [rax]
11c0:	lea	rdi, [rip + 0x2e49]
11c7:	lea	rsi, [rip + 0x2e42]
11ce:	sub	rsi, rdi
11d1:	mov	rax, rsi
11d4:	shr	rsi, 0x3f
11d8:	sar	rax, 3
11dc:	add	rsi, rax
11df:	sar	rsi, 1
11e2:	je	0x11f8
11e4:	mov	rax, qword ptr [rip + 0x2dfd]
11eb:	test	rax, rax
11ee:	je	0x11f8
11f0:	jmp	rax
11f2:	nop	word ptr [rax + rax]
11f8:	ret	
11f9:	nop	dword ptr [rax]
1200:	endbr64	
1204:	cmp	byte ptr [rip + 0x2e1d], 0
120b:	jne	0x1238
120d:	push	rbp
120e:	cmp	qword ptr [rip + 0x2dda], 0
1216:	mov	rbp, rsp
1219:	je	0x1227
121b:	mov	rdi, qword ptr [rip + 0x2de6]
1222:	call	0x10c0
1227:	call	0x1190
122c:	mov	byte ptr [rip + 0x2df5], 1
1233:	pop	rbp
1234:	ret	
1235:	nop	dword ptr [rax]
1238:	ret	
1239:	nop	dword ptr [rax]
1240:	endbr64	
1244:	jmp	0x11c0
1249:	endbr64	
124d:	mov	eax, edi
124f:	shl	eax, 0xd
1252:	xor	eax, edi
1254:	mov	edx, eax
1256:	shr	edx, 0x11
1259:	xor	edx, eax
125b:	mov	eax, edx
125d:	shl	eax, 5
1260:	xor	eax, edx
1262:	ret	
1263:	endbr64	
1267:	imul	eax, edi, 0x19660d
126d:	add	eax, 0x3c6ef35f
1272:	ret	
1273:	endbr64	
1277:	cmp	edi, 1
127a:	je	0x1291
127c:	xor	edx, ecx
127e:	xor	edx, esi
1280:	mov	eax, edx
1282:	xor	eax, r8d
1285:	cmp	edx, r8d
1288:	mov	edx, 0x6d2b79f5
128d:	cmove	eax, edx
1290:	ret	
1291:	mov	eax, ecx
1293:	shr	eax, 8
1296:	xor	eax, edx
1298:	xor	eax, r8d
129b:	xor	eax, esi
129d:	and	eax, 0xff
12a2:	mov	edx, 0xa7
12a7:	cmove	eax, edx
12aa:	ret	
12ab:	endbr64	
12af:	push	rbp
12b0:	mov	rbp, rsp
12b3:	push	rbx
12b4:	sub	rsp, 8
12b8:	mov	rbx, rdx
12bb:	cmp	edi, 1
12be:	je	0x12d6
12c0:	mov	edi, dword ptr [rdx]
12c2:	call	0x1249
12c7:	mov	ecx, eax
12c9:	and	ecx, 1
12cc:	mov	dword ptr [rbx], eax
12ce:	mov	eax, ecx
12d0:	mov	rbx, qword ptr [rbp - 8]
12d4:	leave	
12d5:	ret	
12d6:	mov	ecx, dword ptr [rdx]
12d8:	mov	edx, ecx
12da:	shr	edx, 1
12dc:	movzx	esi, sil
12e0:	xor	esi, edx
12e2:	and	ecx, 1
12e5:	cmovne	edx, esi
12e8:	mov	dword ptr [rbx], edx
12ea:	movzx	eax, dl
12ed:	jmp	0x12cc
12ef:	endbr64	
12f3:	cmp	edi, 1
12f6:	je	0x130d
12f8:	cmp	edi, 2
12fb:	je	0x1311
12fd:	mov	eax, ecx
12ff:	sub	eax, edx
1301:	add	eax, esi
1303:	mov	edx, 0
1308:	div	ecx
130a:	mov	eax, edx
130c:	ret	
130d:	xor	edx, esi
130f:	jmp	0x130a
1311:	lea	eax, [rsi + rdx]
1314:	mov	edx, 0
1319:	div	ecx
131b:	jmp	0x130a
131d:	endbr64	
1321:	mov	r9, rdi
1324:	test	esi, esi
1326:	je	0x135d
1328:	mov	r10d, esi
132b:	mov	eax, 0
1330:	mov	r8d, 0
1336:	sub	esi, 1
1339:	movzx	edi, byte ptr [r9 + rax]
133e:	and	edi, 1
1341:	mov	ecx, esi
1343:	sub	ecx, eax
1345:	cmp	edx, 1
1348:	cmovne	ecx, eax
134b:	shl	edi, cl
134d:	or	r8d, edi
1350:	add	rax, 1
1354:	cmp	rax, r10
1357:	jne	0x1339
1359:	mov	eax, r8d
135c:	ret	
135d:	mov	r8d, esi
1360:	jmp	0x1359
1362:	endbr64	
1366:	mov	r9d, esi
1369:	mov	rax, rdx
136c:	mov	ecx, edi
136e:	shr	ecx, 3
1371:	and	ecx, 1
1374:	mov	edx, edi
1376:	shr	edx, 2
1379:	and	edx, 1
137c:	mov	esi, edi
137e:	and	esi, 1
1381:	mov	r8d, edx
1384:	xor	r8d, ecx
1387:	xor	r8d, esi
138a:	mov	byte ptr [rax], r8b
138d:	shr	edi, 1
138f:	and	edi, 1
1392:	mov	r8d, edi
1395:	xor	r8d, ecx
1398:	xor	r8d, esi
139b:	mov	byte ptr [rax + 1], r8b
139f:	mov	byte ptr [rax + 2], cl
13a2:	mov	ecx, edi
13a4:	xor	ecx, edx
13a6:	xor	ecx, esi
13a8:	mov	byte ptr [rax + 3], cl
13ab:	mov	byte ptr [rax + 4], dl
13ae:	mov	byte ptr [rax + 5], dil
13b2:	mov	byte ptr [rax + 6], sil
13b6:	cmp	r9d, 8
13ba:	je	0x13bd
13bc:	ret	
13bd:	mov	rdx, rax
13c0:	lea	rdi, [rax + 7]
13c4:	mov	ecx, 0
13c9:	movzx	esi, byte ptr [rdx]
13cc:	xor	ecx, esi
13ce:	add	rdx, 1
13d2:	cmp	rdx, rdi
13d5:	jne	0x13c9
13d7:	mov	byte ptr [rax + 7], cl
13da:	ret	
13db:	endbr64	
13df:	test	edx, edx
13e1:	je	0x1474
13e7:	push	rbp
13e8:	mov	rbp, rsp
13eb:	push	r14
13ed:	push	r13
13ef:	push	r12
13f1:	push	rbx
13f2:	mov	r10, rdi
13f5:	mov	r11, rsi
13f8:	mov	esi, edx
13fa:	mov	r9d, ecx
13fd:	mov	ebx, 0
1402:	mov	r8d, 0
1408:	lea	r12d, [rdx - 1]
140c:	mov	r14d, 0
1412:	jmp	0x1453
1414:	imul	eax, esi
1417:	lea	eax, [rax + rdi]
141a:	movzx	eax, byte ptr [r10 + rax]
141f:	mov	ecx, ecx
1421:	mov	byte ptr [r11 + rcx], al
1425:	lea	eax, [rdx + 1]
1428:	cmp	esi, eax
142a:	je	0x1447
142c:	mov	edx, eax
142e:	lea	ecx, [r8 + rdx]
1432:	mov	eax, edx
1434:	cmp	r9d, 3
1438:	jne	0x1414
143a:	mov	eax, r12d
143d:	sub	eax, edx
143f:	test	r13d, r13d
1442:	cmove	eax, edx
1445:	jmp	0x1414
1447:	add	r8d, eax
144a:	lea	eax, [rbx + 1]
144d:	cmp	ebx, edx
144f:	je	0x146b
1451:	mov	ebx, eax
1453:	mov	edi, r12d
1456:	sub	edi, ebx
1458:	cmp	r9d, 2
145c:	cmovne	edi, ebx
145f:	mov	edx, r14d
1462:	mov	r13d, ebx
1465:	and	r13d, 1
1469:	jmp	0x142e
146b:	pop	rbx
146c:	pop	r12
146e:	pop	r13
1470:	pop	r14
1472:	pop	rbp
1473:	ret	
1474:	ret	
1475:	endbr64	
1479:	push	rbp
147a:	mov	rbp, rsp
147d:	push	rbx
147e:	sub	rsp, 8
1482:	mov	rbx, rsi
1485:	cmp	edi, 1
1488:	je	0x1499
148a:	mov	edi, dword ptr [rsi]
148c:	call	0x1263
1491:	mov	dword ptr [rbx], eax
1493:	mov	rbx, qword ptr [rbp - 8]
1497:	leave	
1498:	ret	
1499:	mov	edi, dword ptr [rsi]
149b:	call	0x1249
14a0:	jmp	0x1491
14a2:	endbr64	
14a6:	test	edx, edx
14a8:	je	0x14ca
14aa:	mov	edx, edx
14ac:	mov	eax, 0
14b1:	movzx	ecx, byte ptr [rdi + rax]
14b5:	movzx	r8d, byte ptr [rsi + rax]
14ba:	mov	byte ptr [rdi + rax], r8b
14be:	mov	byte ptr [rsi + rax], cl
14c1:	add	rax, 1
14c5:	cmp	rdx, rax
14c8:	jne	0x14b1
14ca:	ret	
14cb:	endbr64	
14cf:	push	rbp
14d0:	mov	rbp, rsp
14d3:	push	r15
14d5:	push	r14
14d7:	push	r13
14d9:	push	r12
14db:	push	rbx
14dc:	sub	rsp, 0x28
14e0:	mov	dword ptr [rbp - 0x44], edx
14e3:	mov	rax, qword ptr fs:[0x28]
14ec:	mov	qword ptr [rbp - 0x38], rax
14f0:	xor	eax, eax
14f2:	test	ecx, ecx
14f4:	mov	eax, 0x6d2b79f5
14f9:	cmove	ecx, eax
14fc:	mov	dword ptr [rbp - 0x3c], ecx
14ff:	mov	ebx, esi
1501:	sub	ebx, 1
1504:	je	0x1549
1506:	mov	r13, rdi
1509:	mov	r14d, r8d
150c:	mov	eax, ebx
150e:	lea	r12, [rax + rax*4]
1512:	add	r12, rdi
1515:	lea	r15, [rbp - 0x3c]
1519:	mov	rsi, r15
151c:	mov	edi, r14d
151f:	call	0x1475
1524:	lea	ecx, [rbx + 1]
1527:	mov	edx, 0
152c:	div	ecx
152e:	lea	rsi, [rdx + rdx*4]
1532:	add	rsi, r13
1535:	mov	edx, dword ptr [rbp - 0x44]
1538:	mov	rdi, r12
153b:	call	0x14a2
1540:	sub	r12, 5
1544:	sub	ebx, 1
1547:	jne	0x1519
1549:	mov	rax, qword ptr [rbp - 0x38]
154d:	sub	rax, qword ptr fs:[0x28]
1556:	jne	0x1567
1558:	add	rsp, 0x28
155c:	pop	rbx
155d:	pop	r12
155f:	pop	r13
1561:	pop	r14
1563:	pop	r15
1565:	pop	rbp
1566:	ret	
1567:	call	0x1100
156c:	endbr64	
1570:	push	rbp
1571:	mov	rbp, rsp
1574:	push	r15
1576:	push	r14
1578:	push	r13
157a:	push	r12
157c:	push	rbx
157d:	sub	rsp, 0x18
1581:	mov	r14d, esi
1584:	mov	ebx, ecx
1586:	mov	rax, qword ptr fs:[0x28]
158f:	mov	qword ptr [rbp - 0x38], rax
1593:	xor	eax, eax
1595:	mov	dword ptr [rbp - 0x3d], 0
159c:	mov	byte ptr [rbp - 0x39], 0
15a0:	test	esi, esi
15a2:	je	0x15ef
15a4:	mov	r8, rdi
15a7:	lea	rsi, [rbp - 0x3d]
15ab:	mov	r9d, r14d
15ae:	mov	r10d, 0
15b4:	jmp	0x15e4
15b6:	add	byte ptr [rsi], 1
15b9:	add	rax, 1
15bd:	cmp	rax, r9
15c0:	je	0x15d7
15c2:	mov	rcx, qword ptr [r8 + rax*8]
15c6:	cmp	rcx, rdi
15c9:	jl	0x15b6
15cb:	cmp	eax, r10d
15ce:	jae	0x15b9
15d0:	cmp	rcx, rdi
15d3:	jne	0x15b9
15d5:	jmp	0x15b6
15d7:	add	r10, 1
15db:	add	rsi, 1
15df:	cmp	r10, r9
15e2:	je	0x15ef
15e4:	mov	rdi, qword ptr [r8 + r10*8]
15e8:	mov	eax, 0
15ed:	jmp	0x15c2
15ef:	test	ebx, ebx
15f1:	je	0x1649
15f3:	mov	r12, rdx
15f6:	mov	r13d, 0
15fc:	mov	r14d, r14d
15ff:	lea	r15, [rbp - 0x3d]
1603:	mov	rdx, r14
1606:	mov	rsi, r12
1609:	mov	rdi, r15
160c:	call	0x1110
1611:	test	eax, eax
1613:	je	0x1628
1615:	add	r13d, 1
1619:	add	r12, 5
161d:	cmp	ebx, r13d
1620:	jne	0x1603
1622:	mov	r13d, 0xff
1628:	mov	rax, qword ptr [rbp - 0x38]
162c:	sub	rax, qword ptr fs:[0x28]
1635:	jne	0x1651
1637:	mov	eax, r13d
163a:	add	rsp, 0x18
163e:	pop	rbx
163f:	pop	r12
1641:	pop	r13
1643:	pop	r14
1645:	pop	r15
1647:	pop	rbp
1648:	ret	
1649:	mov	r13d, 0xff
164f:	jmp	0x1628
1651:	call	0x1100
1656:	endbr64	
165a:	mov	eax, edi
165c:	cmp	edi, 0x13
165f:	ja	0x16ab
1661:	cmp	edx, 0xc
1664:	ja	0x16ab
1666:	test	edx, edx
1668:	je	0x1699
166a:	mov	r10d, edx
166d:	mov	ecx, 0
1672:	mov	edi, edi
1674:	lea	r8, [rdi + rdi*2]
1678:	lea	rdi, [rip + 0x29e1]
167f:	lea	r9, [rdi + r8*4]
1683:	movzx	r8d, byte ptr [rsi + rcx]
1688:	mov	edi, ecx
168a:	add	rdi, r9
168d:	mov	byte ptr [rdi], r8b
1690:	add	rcx, 1
1694:	cmp	rcx, r10
1697:	jne	0x1683
1699:	mov	ecx, eax
169b:	lea	rsi, [rip + 0x299e]
16a2:	mov	byte ptr [rsi + rcx], dl
16a5:	add	eax, 0x5100
16aa:	ret	
16ab:	mov	eax, 0xffffffff
16b0:	ret	
16b1:	endbr64	
16b5:	push	rbp
16b6:	mov	rbp, rsp
16b9:	cmp	dil, 0x84
16bd:	je	0x174c
16c3:	ja	0x16f2
16c5:	lea	eax, [rdi - 0x22]
16c8:	cmp	al, 0x4b
16ca:	ja	0x182d
16d0:	sub	edi, 0x22
16d3:	cmp	dil, 0x4b
16d7:	ja	0x183b
16dd:	movzx	edi, dil
16e1:	lea	rcx, [rip + 0x91c]
16e8:	movsxd	rax, dword ptr [rcx + rdi*4]
16ec:	add	rax, rcx
16ef:	notrack jmp	rax
16f2:	lea	eax, [rdi + 0x70]
16f5:	cmp	al, 0x45
16f7:	ja	0x1842
16fd:	add	edi, 0x70
1700:	cmp	dil, 0x45
1704:	ja	0x1834
170a:	movzx	edi, dil
170e:	lea	rcx, [rip + 0xa1f]
1715:	movsxd	rax, dword ptr [rcx + rdi*4]
1719:	add	rax, rcx
171c:	notrack jmp	rax
171f:	mov	edi, 0
1724:	call	0x1656
1729:	jmp	0x1840
172e:	mov	edi, 1
1733:	call	0x1656
1738:	jmp	0x1840
173d:	mov	edi, 2
1742:	call	0x1656
1747:	jmp	0x1840
174c:	mov	edi, 3
1751:	call	0x1656
1756:	jmp	0x1840
175b:	mov	edi, 4
1760:	call	0x1656
1765:	jmp	0x1840
176a:	mov	edi, 5
176f:	call	0x1656
1774:	jmp	0x1840
1779:	mov	edi, 6
177e:	call	0x1656
1783:	jmp	0x1840
1788:	mov	edi, 7
178d:	call	0x1656
1792:	jmp	0x1840
1797:	mov	edi, 8
179c:	call	0x1656
17a1:	jmp	0x1840
17a6:	mov	edi, 9
17ab:	call	0x1656
17b0:	jmp	0x1840
17b5:	mov	edi, 0xa
17ba:	call	0x1656
17bf:	jmp	0x1840
17c1:	mov	edi, 0xb
17c6:	call	0x1656
17cb:	jmp	0x1840
17cd:	mov	edi, 0xc
17d2:	call	0x1656
17d7:	jmp	0x1840
17d9:	mov	edi, 0xd
17de:	call	0x1656
17e3:	jmp	0x1840
17e5:	mov	edi, 0xe
17ea:	call	0x1656
17ef:	jmp	0x1840
17f1:	mov	edi, 0xf
17f6:	call	0x1656
17fb:	jmp	0x1840
17fd:	mov	edi, 0x10
1802:	call	0x1656
1807:	jmp	0x1840
1809:	mov	edi, 0x11
180e:	call	0x1656
1813:	jmp	0x1840
1815:	mov	edi, 0x12
181a:	call	0x1656
181f:	jmp	0x1840
1821:	mov	edi, 0x13
1826:	call	0x1656
182b:	jmp	0x1840
182d:	mov	eax, 0xfffffffe
1832:	jmp	0x1840
1834:	mov	eax, 0xfffffffe
1839:	jmp	0x1840
183b:	mov	eax, 0xfffffffe
1840:	pop	rbp
1841:	ret	
1842:	mov	eax, 0xfffffffe
1847:	jmp	0x1840
1849:	endbr64	
184d:	test	esi, esi
184f:	je	0x1892
1851:	mov	r8, rdi
1854:	mov	esi, esi
1856:	add	rdi, rsi
1859:	mov	eax, 0xffffffff
185e:	jmp	0x1869
1860:	add	r8, 1
1864:	cmp	r8, rdi
1867:	je	0x1891
1869:	movzx	edx, byte ptr [r8]
186d:	shl	edx, 8
1870:	xor	eax, edx
1872:	mov	ecx, 8
1877:	lea	edx, [rax + rax]
187a:	xor	dx, 0x1021
187f:	lea	esi, [rax + rax]
1882:	test	ax, ax
1885:	mov	eax, edx
1887:	cmovns	eax, esi
188a:	sub	ecx, 1
188d:	jne	0x1877
188f:	jmp	0x1860
1891:	ret	
1892:	mov	eax, 0xffffffff
1897:	ret	
1898:	endbr64	
189c:	cmp	edi, 7
189f:	ja	0x19cf
18a5:	mov	eax, edi
18a7:	lea	rdx, [rip + 0x99e]
18ae:	movsxd	rax, dword ptr [rdx + rax*4]
18b2:	add	rax, rdx
18b5:	notrack jmp	rax
18b8:	mov	eax, 1
18bd:	cmp	esi, 4
18c0:	je	0x19d4
18c6:	mov	eax, 2
18cb:	cmp	esi, 5
18ce:	je	0x19d4
18d4:	cmp	esi, 3
18d7:	mov	eax, 0x63
18dc:	cmove	eax, edi
18df:	ret	
18e0:	mov	eax, 4
18e5:	cmp	esi, 2
18e8:	je	0x19d4
18ee:	mov	eax, 5
18f3:	cmp	esi, 3
18f6:	je	0x19d4
18fc:	cmp	esi, 1
18ff:	mov	eax, 3
1904:	mov	edx, 0x63
1909:	cmovne	eax, edx
190c:	ret	
190d:	mov	eax, 6
1912:	cmp	esi, 7
1915:	je	0x19d4
191b:	cmp	esi, 8
191e:	mov	eax, 0x63
1923:	mov	edx, 7
1928:	cmove	eax, edx
192b:	ret	
192c:	mov	eax, 9
1931:	cmp	esi, 2
1934:	je	0x19d4
193a:	mov	eax, 0xa
193f:	cmp	esi, 3
1942:	je	0x19d4
1948:	cmp	esi, 1
194b:	mov	eax, 8
1950:	mov	edx, 0x63
1955:	cmovne	eax, edx
1958:	ret	
1959:	mov	eax, 0xb
195e:	cmp	esi, 1
1961:	je	0x19d4
1963:	cmp	esi, 2
1966:	mov	eax, 0x63
196b:	mov	edx, 0xc
1970:	cmove	eax, edx
1973:	ret	
1974:	mov	eax, 0xd
1979:	cmp	esi, 1
197c:	je	0x19d4
197e:	cmp	esi, 2
1981:	mov	eax, 0x63
1986:	mov	edx, 0xe
198b:	cmove	eax, edx
198e:	ret	
198f:	mov	eax, 0xf
1994:	cmp	esi, 1
1997:	je	0x19d4
1999:	cmp	esi, 2
199c:	mov	eax, 0x63
19a1:	mov	edx, 0x10
19a6:	cmove	eax, edx
19a9:	ret	
19aa:	mov	eax, 0x12
19af:	cmp	esi, 2
19b2:	je	0x19d4
19b4:	mov	eax, 0x13
19b9:	cmp	esi, 3
19bc:	je	0x19d4
19be:	cmp	esi, 1
19c1:	mov	eax, 0x11
19c6:	mov	edx, 0x63
19cb:	cmovne	eax, edx
19ce:	ret	
19cf:	mov	eax, 0x63
19d4:	ret	
19d5:	endbr64	
19d9:	push	rbp
19da:	mov	rbp, rsp
19dd:	push	r15
19df:	push	r14
19e1:	push	r13
19e3:	push	r12
19e5:	push	rbx
19e6:	sub	rsp, 0x48
19ea:	mov	rax, qword ptr fs:[0x28]
19f3:	mov	qword ptr [rbp - 0x38], rax
19f7:	xor	eax, eax
19f9:	cmp	edi, 2
19fc:	jne	0x1a6e
19fe:	mov	rdi, qword ptr [rsi + 8]
1a02:	lea	rsi, [rip + 0x88e]
1a09:	call	0x1140
1a0e:	mov	rbx, rax
1a11:	test	rax, rax
1a14:	je	0x1c7f
1a1a:	mov	edi, 0x10000
1a1f:	call	0x1120
1a24:	mov	r13, rax
1a27:	mov	rcx, rbx
1a2a:	mov	edx, 0x10000
1a2f:	mov	esi, 1
1a34:	mov	rdi, rax
1a37:	call	0x10e0
1a3c:	mov	r15, rax
1a3f:	mov	qword ptr [rbp - 0x60], rax
1a43:	mov	rdi, rbx
1a46:	call	0x10f0
1a4b:	mov	rax, r15
1a4e:	cmp	r15, 0xa
1a52:	jbe	0x1b79
1a58:	sub	rax, 0xa
1a5c:	mov	qword ptr [rbp - 0x58], rax
1a60:	mov	ebx, 0
1a65:	mov	dword ptr [rbp - 0x64], 0
1a6c:	jmp	0x1aaa
1a6e:	mov	rcx, qword ptr [rip + 0x25ab]
1a75:	mov	edx, 0x26
1a7a:	mov	esi, 1
1a7f:	lea	rdi, [rip + 0x7ea]
1a86:	call	0x1150
1a8b:	mov	eax, 0x40
1a90:	jmp	0x1c61
1a95:	add	dword ptr [rbp - 0x64], 1
1a99:	add	rbx, 1
1a9d:	mov	rax, qword ptr [rbp - 0x58]
1aa1:	cmp	rbx, rax
1aa4:	je	0x1b80
1aaa:	lea	r15, [r13 + rbx]
1aaf:	mov	edx, 4
1ab4:	lea	rsi, [rip + 0x7df]
1abb:	mov	rdi, r15
1abe:	call	0x1110
1ac3:	test	eax, eax
1ac5:	jne	0x1a99
1ac7:	movzx	r12d, byte ptr [r13 + rbx + 6]
1acd:	shl	r12d, 8
1ad1:	movzx	eax, byte ptr [r13 + rbx + 5]
1ad7:	or	r12d, eax
1ada:	cmp	r12d, 9
1ade:	jbe	0x1a99
1ae0:	mov	r14d, r12d
1ae3:	add	r14, rbx
1ae6:	cmp	qword ptr [rbp - 0x60], r14
1aea:	jb	0x1a99
1aec:	sub	r12d, 2
1af0:	mov	esi, r12d
1af3:	mov	rdi, r15
1af6:	call	0x1849
1afb:	mov	edx, eax
1afd:	movzx	eax, byte ptr [r13 + r14 - 2]
1b03:	shl	eax, 8
1b06:	movzx	ecx, byte ptr [r13 + r14 - 1]
1b0c:	or	eax, ecx
1b0e:	cmp	dx, ax
1b11:	jne	0x1a99
1b13:	cmp	r12d, 0xa
1b17:	jbe	0x1a95
1b1d:	movzx	edi, byte ptr [r13 + rbx + 8]
1b23:	movzx	edx, byte ptr [r13 + rbx + 9]
1b29:	lea	r14d, [rdx + 0xa]
1b2d:	cmp	r12d, r14d
1b30:	jb	0x1a95
1b36:	mov	esi, 0xa
1b3b:	mov	esi, esi
1b3d:	add	rsi, rbx
1b40:	add	rsi, r13
1b43:	movzx	edi, dil
1b47:	call	0x16b1
1b4c:	lea	esi, [r14 + 2]
1b50:	cmp	esi, r12d
1b53:	jae	0x1a95
1b59:	mov	r14d, r14d
1b5c:	add	r14, rbx
1b5f:	movzx	edi, byte ptr [r13 + r14]
1b65:	movzx	edx, byte ptr [r13 + r14 + 1]
1b6b:	lea	r14d, [rsi + rdx]
1b6f:	cmp	r12d, r14d
1b72:	jae	0x1b3b
1b74:	jmp	0x1a95
1b79:	mov	dword ptr [rbp - 0x64], 0
1b80:	mov	r8d, 0
1b86:	mov	ecx, 0x51
1b8b:	mov	edx, 0x37
1b90:	mov	esi, 0x19
1b95:	mov	edi, 2
1b9a:	call	0x1273
1b9f:	mov	dword ptr [rbp - 0x48], eax
1ba2:	mov	qword ptr [rbp - 0x40], 0
1baa:	lea	r14, [rbp - 0x40]
1bae:	mov	rdx, r14
1bb1:	mov	esi, 8
1bb6:	mov	edi, 9
1bbb:	call	0x1362
1bc0:	movzx	esi, byte ptr [rip + 0x24b1]
1bc7:	movzx	esi, sil
1bcb:	mov	edi, 0
1bd0:	call	0x1898
1bd5:	xor	eax, 0x4f
1bd8:	mov	dword ptr [rbp - 0x44], eax
1bdb:	lea	rdx, [rbp - 0x48]
1bdf:	mov	esi, 0x51
1be4:	mov	edi, 2
1be9:	call	0x12ab
1bee:	mov	ebx, eax
1bf0:	mov	ecx, 0x10
1bf5:	mov	edx, 2
1bfa:	mov	esi, 1
1bff:	mov	edi, 2
1c04:	call	0x12ef
1c09:	mov	r12d, eax
1c0c:	mov	edx, 1
1c11:	mov	esi, 4
1c16:	mov	rdi, r14
1c19:	call	0x131d
1c1e:	mov	edx, eax
1c20:	mov	eax, dword ptr [rbp - 0x44]
1c23:	xor	ebx, edx
1c25:	xor	ebx, eax
1c27:	xor	ebx, r12d
1c2a:	xor	ebx, 0x6f
1c2d:	mov	dword ptr [rbp - 0x44], ebx
1c30:	mov	ecx, dword ptr [rbp - 0x44]
1c33:	movzx	ecx, cl
1c36:	mov	ebx, dword ptr [rbp - 0x64]
1c39:	mov	edx, ebx
1c3b:	lea	rsi, [rip + 0x65d]
1c42:	mov	edi, 2
1c47:	mov	eax, 0
1c4c:	call	0x1130
1c51:	mov	rdi, r13
1c54:	call	0x10d0
1c59:	cmp	ebx, 1
1c5c:	sbb	eax, eax
1c5e:	and	eax, 0x41
1c61:	mov	rdx, qword ptr [rbp - 0x38]
1c65:	sub	rdx, qword ptr fs:[0x28]
1c6e:	jne	0x1c86
1c70:	add	rsp, 0x48
1c74:	pop	rbx
1c75:	pop	r12
1c77:	pop	r13
1c79:	pop	r14
1c7b:	pop	r15
1c7d:	pop	rbp
1c7e:	ret	
1c7f:	mov	eax, 0x42
1c84:	jmp	0x1c61
1c86:	call	0x1100