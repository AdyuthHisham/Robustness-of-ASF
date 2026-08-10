| Line# | Function | Change Summary | Category |
|-------|----------|---------------|----------|
| L10 | module-level | -     ldr64         : (N, M)   numpy — [x, y, z, ...] (M >= 3) | c |
| L10 | module-level | +     ldr64         : (N, M)   numpy — [x, y, z, intensity, ring, ...] (M >= 3) | c |
| L13 | module-level | +  | c |
| L14 | module-level | + TAXONOMY (Rev 2): 12 effects, 4 per modality: | c |
| L15 | module-level | +   Radar:     frame_deletion, noise_induced_shifts, loss_partial, loss_complete | c |
| L16 | module-level | +   LiDAR:     frame_deletion, gaussian_noise,        loss_partial, loss_complete | c |
| L17 | module-level | +   Camera:    frame_deletion, gaussian_noise,        loss_partial, loss_complete | c |
| L18 | module-level | +  | c |
| L19 | module-level | + Legacy effects from Rev 1 (18-effect design) are preserved below under | c |
| L20 | module-level | + "# LEGACY EFFECTS" for manual import but are NOT loaded into the active | c |
| L21 | module-level | + registries or used by NoiseInjector. | c |
| L26 | module-level | -     from .config import EffectConfig  # when loaded as part of dataseta.effects package | c |
| L35 | module-level | +     from .config import EffectConfig  # when loaded as part of datasets.effects package | c |
| L35 | _sub_rng | - def _sub_rng(master: np.random.Generator, name: str, seed_offset: int = 0) -> np.random.Generator: | c |
| L36 | _sub_rng | -     """Derive a deterministic sub-generator from the master RNG and effect name.""" | c |
| L37 | _sub_rng | -     sub_seed = hash((master.bit_generator.state["state"]["state"], name, seed_offset)) & 0xFFFFFFFF | c |
| L38 | _sub_rng | -     return np.random.default_rng(sub_seed) | c |
| L44 | _sub_rng | + def _sub_rng(master: np.random.Generator, name: str, seed_offset: int = 0) -> np.random.Generator: | c |
| L45 | _sub_rng | +     """Derive a deterministic sub-generator from the master RNG and effect name.""" | c |
| L46 | _sub_rng | +     sub_seed = hash((master.bit_generator.state["state"]["state"], name, seed_offset)) & 0xFFFFFFFF | c |
| L47 | _sub_rng | +     return np.random.default_rng(sub_seed) | c |
| L48 | _sub_rng | +  | c |
| L49 | _sub_rng | +  | c |
| L50 | _has_key | + def _has_key(d: dict, key: str) -> bool: | c |
| L51 | _has_key | +     """True if the dict_item has this sensor key and it's not None (data is present).""" | c |
| L52 | _has_key | +     return key in d and d[key] is not None | c |
| L53 | _has_key | +  | c |
| L54 | _has_key | +  | c |
| L55 | _set_none | + def _set_none(d: dict, keys: list[str]) -> None: | c |
| L56 | _set_none | +     """Set the given keys to None (sensor blackout / frame deleted).""" | c |
| L57 | _set_none | +     for k in keys: | c |
| L58 | _set_none | +         if k in d: | c |
| L59 | _set_none | +             d[k] = None | c |
| L60 | _set_none | +  | c |
| L61 | _set_none | +  | c |
| L62 | _get_modality_idx | + def _get_modality_idx(d: dict, modality: str) -> int | None: | c |
| L63 | _get_modality_idx | +     """Extract the frame index for a modality from dict_item['meta']['idx'].""" | c |
| L64 | _get_modality_idx | +     meta = d.get("meta", {}) | c |
| L65 | _get_modality_idx | +     idx_dict = meta.get("idx", {}) | c |
| L66 | _get_modality_idx | +     return idx_dict.get(modality, None) | c |
| L67 | _get_modality_idx | +  | c |
| L68 | _get_modality_idx | +  | c |
| L69 | _get_modality_idx | + # ══════════════════════════════════════════════ | c |
| L70 | _get_modality_idx | + # SHARED: Frame deletion (deterministic + random per modality) | c |
| L71 | _get_modality_idx | + # ══════════════════════════════════════════════ | c |
| L72 | _get_modality_idx | +  | c |
| L73 | _get_modality_idx | +  | c |
| L74 | _frame_deletion_check | + def _frame_deletion_check(params: dict, rng: np.random.Generator, | c |
| L75 | _frame_deletion_check | +                            frame_index: int | None = None) -> bool: | c |
| L76 | _frame_deletion_check | +     """Return True if this frame should be deleted (decider shared by all modalities). | c |
| L77 | _frame_deletion_check | +  | c |
| L78 | _frame_deletion_check | +     Parameters (from params dict): | c |
| L79 | _frame_deletion_check | +         mode : str — 'deterministic' or 'random' (default: 'random') | c |
| L80 | _frame_deletion_check | +         interval : int — delete every Nth frame (mode='deterministic', no index_list) | c |
| L81 | _frame_deletion_check | +         index_list : list[int] — explicit indices to delete (mode='deterministic') | c |
| L82 | _frame_deletion_check | +         p : float — per-frame deletion probability (mode='random', default: 0.1) | c |
| L83 | _frame_deletion_check | +         frame_index : int | None — caller-provided frame index for deterministic mode | c |
| L84 | _frame_deletion_check | +     """ | c |
| L85 | _frame_deletion_check | +     mode = params.get("mode", "random") | c |
| L86 | _frame_deletion_check | +     if mode == "deterministic": | c |
| L87 | _frame_deletion_check | +         index_list = params.get("index_list", None) | c |
| L88 | _frame_deletion_check | +         if index_list is not None: | c |
| L89 | _frame_deletion_check | +             # index_list mode: delete if frame_index is in the list | c |
| L90 | _frame_deletion_check | +             if frame_index is None: | c |
| L91 | _frame_deletion_check | +                 # Can't check list without frame_index — don't delete (graceful skip) | c |
| L92 | _frame_deletion_check | +                 return False | c |
| L93 | _frame_deletion_check | +             return int(frame_index) in index_list | c |
| L94 | _frame_deletion_check | +         else: | c |
| L95 | _frame_deletion_check | +             # interval mode: delete every Nth frame | c |
| L96 | _frame_deletion_check | +             interval = params.get("interval", 10) | c |
| L97 | _frame_deletion_check | +             if frame_index is None: | c |
| L98 | _frame_deletion_check | +                 return False  # no frame index available — don't delete | c |
| L99 | _frame_deletion_check | +             return int(frame_index) % interval == 0 | c |
| L100 | _frame_deletion_check | +     else:  # 'random' | c |
| L101 | _frame_deletion_check | +         p = params.get("p", 0.1) | c |
| L102 | _frame_deletion_check | +         return rng.uniform() < p | c |
| L103 | _frame_deletion_check | +  | c |
| L104 | _frame_deletion_check | +  | c |
| L105 | _frame_deletion_check | + # ────────────────────────────────────────────── | c |
| L106 | _frame_deletion_check | + # RADAR EFFECTS  (4 effects) | c |
| L107 | _frame_deletion_check | + # ────────────────────────────────────────────── | c |
| L108 | _frame_deletion_check | +  | c |
| L109 | _frame_deletion_check | +  | c |
| L110 | radar_frame_deletion | + def radar_frame_deletion(dict_item: dict, params: dict, rng: np.random.Generator) -> dict: | c |
| L111 | radar_frame_deletion | +     """R1 — Radar frame deletion (deterministic or random). | c |
| L112 | radar_frame_deletion | +  | c |
| L113 | radar_frame_deletion | +     When fired, sets ``rdr_sparse``, ``rdr_polar_3d``, and ``pc100p`` to None. | c |
| L114 | radar_frame_deletion | +     Frame index read from ``dict_item['meta']['idx']['rdr']`` for deterministic mode. | c |
| L115 | radar_frame_deletion | +     """ | c |
| L116 | radar_frame_deletion | +     frame_index = _get_modality_idx(dict_item, "rdr") | c |
| L117 | radar_frame_deletion | +     if _frame_deletion_check(params, rng, frame_index): | c |
| L118 | radar_frame_deletion | +         _set_none(dict_item, ["rdr_sparse", "rdr_polar_3d", "pc100p"]) | c |
| L119 | radar_frame_deletion | +     return dict_item | c |
| L120 | radar_frame_deletion | +  | c |
| L121 | radar_frame_deletion | +  | c |
| L122 | radar_noise_induced_shifts | + def radar_noise_induced_shifts(dict_item: dict, params: dict, rng: np.random.Generator) -> dict: | c |
| L123 | radar_noise_induced_shifts | +     """R2 — Shift radar detection positions by a noise process. | c |
| L124 | radar_noise_induced_shifts | +  | c |
| L125 | radar_noise_induced_shifts | +     Each point in ``rdr_sparse[:, :3]`` and ``pc100p[:, :3]`` is displaced | c |
| L126 | radar_noise_induced_shifts | +     by a random vector.  This is a *coordinate shift* effect — distinct from | c |
| L127 | radar_noise_induced_shifts | +     additive power noise (old power_gaussian_noise) and distinct from azimuth | c |
| L128 | radar_noise_induced_shifts | +     jitter (old azimuth_jitter). | c |
| L129 | radar_noise_induced_shifts | +  | c |
| L130 | radar_noise_induced_shifts | +     Parameters | c |
| L131 | radar_noise_induced_shifts | +     ---------- | c |
| L132 | radar_noise_induced_shifts | +     shift_std : float, optional | c |
| L133 | radar_noise_induced_shifts | +         Standard deviation of displacement in metres (default 1.0). | c |
| L134 | radar_noise_induced_shifts | +     distribution : str, optional | c |
| L135 | radar_noise_induced_shifts | +         'gaussian' (default) or 'uniform'. | c |
| L136 | radar_noise_induced_shifts | +     clip_radius : float, optional | c |
| L137 | radar_noise_induced_shifts | +         Max displacement radius in metres.  If set, displacements exceeding | c |
| L138 | radar_noise_induced_shifts | +         this are clipped to the radius (direction preserved). | c |
| L139 | radar_noise_induced_shifts | +     """ | c |
| L140 | radar_noise_induced_shifts | +     shift_std = params.get("shift_std", 1.0) | c |
| L141 | radar_noise_induced_shifts | +     distribution = params.get("distribution", "gaussian") | c |
| L142 | radar_noise_induced_shifts | +     clip_radius = params.get("clip_radius", None) | c |
| L143 | radar_noise_induced_shifts | +  | c |
| L144 | radar_noise_induced_shifts | +     for key in ["rdr_sparse", "pc100p"]: | c |
| L145 | radar_noise_induced_shifts | +         if _has_key(dict_item, key) and dict_item[key].shape[1] >= 3: | c |
| L146 | radar_noise_induced_shifts | +             arr = dict_item[key] | c |
| L147 | radar_noise_induced_shifts | +             n = len(arr) | c |
| L148 | radar_noise_induced_shifts | +             # Sample displacement vectors | c |
| L149 | radar_noise_induced_shifts | +             if distribution == "uniform": | c |
| L150 | radar_noise_induced_shifts | +                 # Uniform in a sphere of radius shift_std*sqrt(3) ≈ covering | c |
| L151 | radar_noise_induced_shifts | +                 # a cube of side 2*shift_std, then optionally clip | c |
| L152 | radar_noise_induced_shifts | +                 dx = rng.uniform(-shift_std, shift_std, size=n) | c |
| L153 | radar_noise_induced_shifts | +                 dy = rng.uniform(-shift_std, shift_std, size=n) | c |
| L154 | radar_noise_induced_shifts | +                 dz = rng.uniform(-shift_std, shift_std, size=n) | c |
| L155 | radar_noise_induced_shifts | +             else:  # 'gaussian' | c |
| L156 | radar_noise_induced_shifts | +                 dx = rng.normal(0.0, shift_std, size=n) | c |
| L157 | radar_noise_induced_shifts | +                 dy = rng.normal(0.0, shift_std, size=n) | c |
| L158 | radar_noise_induced_shifts | +                 dz = rng.normal(0.0, shift_std, size=n) | c |
| L159 | radar_noise_induced_shifts | +  | c |
| L160 | radar_noise_induced_shifts | +             # Optional clip to max radius | c |
| L161 | radar_noise_induced_shifts | +             if clip_radius is not None and clip_radius > 0: | c |
| L162 | radar_noise_induced_shifts | +                 disp = np.column_stack([dx, dy, dz]) | c |
| L163 | radar_noise_induced_shifts | +                 dist = np.linalg.norm(disp, axis=1) | c |
| L164 | radar_noise_induced_shifts | +                 overshoot = dist > clip_radius | c |
| L165 | radar_noise_induced_shifts | +                 if np.any(overshoot): | c |
| L166 | radar_noise_induced_shifts | +                     scale = np.where(overshoot, clip_radius / np.maximum(dist, 1e-12), 1.0) | c |
| L167 | radar_noise_induced_shifts | +                     disp = disp * scale[:, None] | c |
| L168 | radar_noise_induced_shifts | +                     dx, dy, dz = disp[:, 0], disp[:, 1], disp[:, 2] | c |
| L169 | radar_noise_induced_shifts | +  | c |
| L170 | radar_noise_induced_shifts | +             arr[:, 0] += dx | c |
| L171 | radar_noise_induced_shifts | +             arr[:, 1] += dy | c |
| L172 | radar_noise_induced_shifts | +             arr[:, 2] += dz | c |
| L173 | radar_noise_induced_shifts | +  | c |
| L174 | radar_noise_induced_shifts | +     return dict_item | c |
| L175 | radar_noise_induced_shifts | +  | c |
| L176 | radar_noise_induced_shifts | +  | c |
| L177 | radar_loss_partial | + def radar_loss_partial(dict_item: dict, params: dict, rng: np.random.Generator) -> dict: | c |
| L178 | radar_loss_partial | +     """R3 — Partial radar data loss by Bernoulli sampling on detections. | c |
| L179 | radar_loss_partial | +  | c |
| L180 | radar_loss_partial | +     Each point in ``rdr_sparse`` and ``pc100p`` is independently dropped | c |
| L181 | radar_loss_partial | +     with probability ``fraction``. | c |
| L182 | radar_loss_partial | +  | c |
| L183 | radar_loss_partial | +     Parameters | c |
| L184 | radar_loss_partial | +     ---------- | c |
| L185 | radar_loss_partial | +     fraction : float, optional | c |
| L186 | radar_loss_partial | +         Fraction of points/returns to remove (default 0.3). | c |
| L187 | radar_loss_partial | +     """ | c |
| L188 | radar_loss_partial | +     fraction = params.get("fraction", 0.3) | c |
| L189 | radar_loss_partial | +     for key in ["rdr_sparse", "pc100p"]: | c |
| L190 | radar_loss_partial | +         if _has_key(dict_item, key): | c |
| L191 | radar_loss_partial | +             arr = dict_item[key] | c |
| L192 | radar_loss_partial | +             n = len(arr) | c |
| L193 | radar_loss_partial | +             keep = rng.uniform(size=n) >= fraction | c |
| L194 | radar_loss_partial | +             dict_item[key] = arr[keep] | c |
| L195 | radar_loss_partial | +     return dict_item | c |
| L196 | radar_loss_partial | +  | c |
| L197 | radar_loss_partial | +  | c |
| L198 | radar_loss_complete | + def radar_loss_complete(dict_item: dict, params: dict, rng: np.random.Generator) -> dict: | c |
| L199 | radar_loss_complete | +     """R4 — Full radar data blackout for this frame. | c |
| L200 | radar_loss_complete | +  | c |
| L201 | radar_loss_complete | +     Sets ``rdr_sparse``, ``rdr_polar_3d``, and ``pc100p`` to None. | c |
| L202 | radar_loss_complete | +     Semantically distinct from ``loss_partial(fraction=1.0)`` — this | c |
| L203 | radar_loss_complete | +     represents a total sensor blackout, not extreme sampling. | c |
| L204 | radar_loss_complete | +  | c |
| L205 | radar_loss_complete | +     Parameters: (none required) | c |
| L206 | radar_loss_complete | +     """ | c |
| L207 | radar_loss_complete | +     _set_none(dict_item, ["rdr_sparse", "rdr_polar_3d", "pc100p"]) | c |
| L208 | radar_loss_complete | +     return dict_item | c |
| L209 | radar_loss_complete | +  | c |
| L210 | radar_loss_complete | +  | c |
| L211 | radar_loss_complete | + # ────────────────────────────────────────────── | c |
| L212 | radar_loss_complete | + # LIDAR EFFECTS  (4 effects) | c |
| L213 | radar_loss_complete | + # ────────────────────────────────────────────── | c |
| L214 | radar_loss_complete | +  | c |
| L215 | radar_loss_complete | +  | c |
| L216 | lidar_frame_deletion | + def lidar_frame_deletion(dict_item: dict, params: dict, rng: np.random.Generator) -> dict: | c |
| L217 | lidar_frame_deletion | +     """L1 — LiDAR frame deletion. | c |
| L218 | lidar_frame_deletion | +  | c |
| L219 | lidar_frame_deletion | +     When fired, sets ``ldr64`` to None. | c |
| L220 | lidar_frame_deletion | +     Frame index read from ``dict_item['meta']['idx']['ldr']``. | c |
| L221 | lidar_frame_deletion | +     """ | c |
| L222 | lidar_frame_deletion | +     frame_index = _get_modality_idx(dict_item, "ldr") | c |
| L223 | lidar_frame_deletion | +     if _frame_deletion_check(params, rng, frame_index): | c |
| L224 | lidar_frame_deletion | +         _set_none(dict_item, ["ldr64"]) | c |
| L225 | lidar_frame_deletion | +     return dict_item | c |
| L226 | lidar_frame_deletion | +  | c |
| L227 | lidar_frame_deletion | +  | c |
| L228 | lidar_gaussian_noise | + def lidar_gaussian_noise(dict_item: dict, params: dict, rng: np.random.Generator) -> dict: | c |
| L229 | lidar_gaussian_noise | +     """L2 — Additive Gaussian noise to LiDAR positions and intensity. | c |
| L230 | lidar_gaussian_noise | +  | c |
| L231 | lidar_gaussian_noise | +     Adds independent N(0, sigma) noise to (x, y, z) coordinates and | c |
| L232 | lidar_gaussian_noise | +     optionally to the intensity channel (column 3 in ``ldr64``). | c |
| L233 | lidar_gaussian_noise | +  | c |
| L234 | lidar_gaussian_noise | +     Parameters | c |
| L235 | lidar_gaussian_noise | +     ---------- | c |
| L236 | lidar_gaussian_noise | +     sigma_xy : float, optional | c |
| L237 | lidar_gaussian_noise | +         Std dev of noise in x and y (metres, default 0.1). | c |
| L238 | lidar_gaussian_noise | +     sigma_z : float, optional | c |
| L239 | lidar_gaussian_noise | +         Std dev of noise in z (metres), defaults to sigma_xy. | c |
| L240 | lidar_gaussian_noise | +     sigma_intensity : float, optional | c |
| L241 | lidar_gaussian_noise | +         Std dev of noise on intensity channel (default 0.0 — no noise). | c |
| L242 | lidar_gaussian_noise | +     """ | c |
| L243 | lidar_gaussian_noise | +     sigma_xy = params.get("sigma_xy", 0.1) | c |
| L244 | lidar_gaussian_noise | +     sigma_z = params.get("sigma_z", sigma_xy) | c |
| L245 | lidar_gaussian_noise | +     sigma_intensity = params.get("sigma_intensity", 0.0) | c |
| L246 | lidar_gaussian_noise | +  | c |
| L247 | lidar_gaussian_noise | +     if _has_key(dict_item, "ldr64"): | c |
| L248 | lidar_gaussian_noise | +         pc = dict_item["ldr64"] | c |
| L249 | lidar_gaussian_noise | +         n = len(pc) | c |
| L250 | lidar_gaussian_noise | +         # Position noise | c |
| L251 | lidar_gaussian_noise | +         noise_xy = rng.normal(0.0, sigma_xy, size=(n, 2)) | c |
| L252 | lidar_gaussian_noise | +         noise_z = rng.normal(0.0, sigma_z, size=n) | c |
| L253 | lidar_gaussian_noise | +         pc[:, 0] += noise_xy[:, 0] | c |
| L254 | lidar_gaussian_noise | +         pc[:, 1] += noise_xy[:, 1] | c |
| L255 | lidar_gaussian_noise | +         pc[:, 2] += noise_z | c |
| L256 | lidar_gaussian_noise | +         # Optional intensity noise (column 3) | c |
| L257 | lidar_gaussian_noise | +         if sigma_intensity > 0.0 and pc.shape[1] >= 4: | c |
| L258 | lidar_gaussian_noise | +             noise_intensity = rng.normal(0.0, sigma_intensity, size=n) | c |
| L259 | lidar_gaussian_noise | +             pc[:, 3] += noise_intensity | c |
| L260 | lidar_gaussian_noise | +  | c |
| L261 | lidar_gaussian_noise | +     return dict_item | c |
| L262 | lidar_gaussian_noise | +  | c |
| L263 | lidar_gaussian_noise | +  | c |
| L264 | lidar_loss_partial | + def lidar_loss_partial(dict_item: dict, params: dict, rng: np.random.Generator) -> dict: | c |
| L265 | lidar_loss_partial | +     """L3 — Partial LiDAR data loss by Bernoulli sampling. | c |
| L266 | lidar_loss_partial | +  | c |
| L267 | lidar_loss_partial | +     Each point in ``ldr64`` independently dropped with probability ``fraction``. | c |
| L268 | lidar_loss_partial | +  | c |
| L269 | lidar_loss_partial | +     Parameters | c |
| L270 | lidar_loss_partial | +     ---------- | c |
| L271 | lidar_loss_partial | +     fraction : float, optional | c |
| L272 | lidar_loss_partial | +         Fraction of points to remove (default 0.3). | c |
| L273 | lidar_loss_partial | +     """ | c |
| L274 | lidar_loss_partial | +     fraction = params.get("fraction", 0.3) | c |
| L275 | lidar_loss_partial | +     if _has_key(dict_item, "ldr64"): | c |
| L276 | lidar_loss_partial | +         n = len(dict_item["ldr64"]) | c |
| L277 | lidar_loss_partial | +         keep = rng.uniform(size=n) >= fraction | c |
| L278 | lidar_loss_partial | +         dict_item["ldr64"] = dict_item["ldr64"][keep] | c |
| L279 | lidar_loss_partial | +     return dict_item | c |
| L280 | lidar_loss_partial | +  | c |
| L281 | lidar_loss_partial | +  | c |
| L282 | lidar_loss_complete | + def lidar_loss_complete(dict_item: dict, params: dict, rng: np.random.Generator) -> dict: | c |
| L283 | lidar_loss_complete | +     """L4 — Full LiDAR blackout. | c |
| L284 | lidar_loss_complete | +  | c |
| L285 | lidar_loss_complete | +     Sets ``ldr64`` to None. | c |
| L286 | lidar_loss_complete | +  | c |
| L287 | lidar_loss_complete | +     Parameters: (none required) | c |
| L288 | lidar_loss_complete | +     """ | c |
| L289 | lidar_loss_complete | +     _set_none(dict_item, ["ldr64"]) | c |
| L290 | lidar_loss_complete | +     return dict_item | c |
| L291 | lidar_loss_complete | +  | c |
| L292 | lidar_loss_complete | +  | c |
| L293 | lidar_loss_complete | + # ────────────────────────────────────────────── | c |
| L294 | lidar_loss_complete | + # CAMERA EFFECTS  (4 effects) | c |
| L295 | lidar_loss_complete | + # ────────────────────────────────────────────── | c |
| L296 | lidar_loss_complete | +  | c |
| L297 | lidar_loss_complete | +  | c |
| L298 | _camera_keys | + def _camera_keys(d: dict) -> list[str]: | c |
| L299 | _camera_keys | +     """Return camera-image keys in the dict_item (batched torch.Tensor).""" | c |
| L300 | _camera_keys | +     known = {"front0", "front1", "left0", "left1", "right0", "right1", "rear0", "rear1"} | c |
| L301 | _camera_keys | +     return [k for k in known if k in d and isinstance(d[k], torch.Tensor)] | c |
| L302 | _camera_keys | +  | c |
| L303 | _camera_keys | +  | c |
| L304 | _to_nhwc | + def _to_nhwc(img: torch.Tensor) -> np.ndarray: | c |
| L305 | _to_nhwc | +     """Convert (3, H, W) normalized torch.Tensor → (H, W, 3) uint8 numpy.""" | c |
| L306 | _to_nhwc | +     img_np = img.cpu().numpy().transpose(1, 2, 0)  # (H, W, 3) | c |
| L307 | _to_nhwc | +     mean = np.array([0.485, 0.456, 0.406], dtype=np.float32) | c |
| L308 | _to_nhwc | +     std = np.array([0.229, 0.224, 0.225], dtype=np.float32) | c |
| L309 | _to_nhwc | +     img_np = img_np * std + mean | c |
| L310 | _to_nhwc | +     img_np = np.clip(img_np * 255.0, 0, 255).astype(np.uint8) | c |
| L311 | _to_nhwc | +     return img_np | c |
| L312 | _to_nhwc | +  | c |
| L313 | _to_nhwc | +  | c |
| L314 | _from_nhwc | + def _from_nhwc(arr: np.ndarray) -> torch.Tensor: | c |
| L315 | _from_nhwc | +     """Convert (H, W, 3) uint8 numpy → (3, H, W) normalized torch.Tensor.""" | c |
| L316 | _from_nhwc | +     img_f = arr.astype(np.float32) / 255.0 | c |
| L317 | _from_nhwc | +     mean = np.array([0.485, 0.456, 0.406], dtype=np.float32) | c |
| L318 | _from_nhwc | +     std = np.array([0.229, 0.224, 0.225], dtype=np.float32) | c |
| L319 | _from_nhwc | +     img_f = (img_f - mean) / std | c |
| L320 | _from_nhwc | +     return torch.from_numpy(img_f.transpose(2, 0, 1)) | c |
| L321 | _from_nhwc | +  | c |
| L322 | _from_nhwc | +  | c |
| L323 | _zero_camera_tensor | + def _zero_camera_tensor(img: torch.Tensor) -> torch.Tensor: | c |
| L324 | _zero_camera_tensor | +     """Return a zero-filled tensor in normalized space ≈ black pixel values. | c |
| L325 | _zero_camera_tensor | +  | c |
| L326 | _zero_camera_tensor | +     Black in uint8 (0,0,0) maps to approx (-mean/std) = (-2.12, -2.04, -1.80). | c |
| L327 | _zero_camera_tensor | +     """ | c |
| L328 | _zero_camera_tensor | +     c, h, w = img.shape | c |
| L329 | _zero_camera_tensor | +     mean = torch.tensor([0.485, 0.456, 0.406], device=img.device).view(3, 1, 1) | c |
| L330 | _zero_camera_tensor | +     std = torch.tensor([0.229, 0.224, 0.225], device=img.device).view(3, 1, 1) | c |
| L331 | _zero_camera_tensor | +     black = (torch.zeros_like(img) - mean) / std | c |
| L332 | _zero_camera_tensor | +     return black | c |
| L333 | _zero_camera_tensor | +  | c |
| L334 | _zero_camera_tensor | +  | c |
| L335 | camera_frame_deletion | + def camera_frame_deletion(dict_item: dict, params: dict, rng: np.random.Generator) -> dict: | c |
| L336 | camera_frame_deletion | +     """C1 — Camera frame deletion. | c |
| L337 | camera_frame_deletion | +  | c |
| L338 | camera_frame_deletion | +     When fired, all camera-image keys are replaced with a zero-filled | c |
| L339 | camera_frame_deletion | +     normalized tensor (black frame). Frame index read from | c |
| L340 | camera_frame_deletion | +     ``dict_item['meta']['idx']['cam']``. | c |
| L341 | camera_frame_deletion | +     """ | c |
| L342 | camera_frame_deletion | +     frame_index = _get_modality_idx(dict_item, "cam") | c |
| L343 | camera_frame_deletion | +     if _frame_deletion_check(params, rng, frame_index): | c |
| L344 | camera_frame_deletion | +         for k in _camera_keys(dict_item): | c |
| L345 | camera_frame_deletion | +             dict_item[k] = _zero_camera_tensor(dict_item[k]) | c |
| L346 | camera_frame_deletion | +     return dict_item | c |
| L347 | camera_frame_deletion | +  | c |
| L348 | camera_frame_deletion | +  | c |
| L349 | camera_gaussian_noise | + def camera_gaussian_noise(dict_item: dict, params: dict, rng: np.random.Generator) -> dict: | c |
| L350 | camera_gaussian_noise | +     """C2 — Additive Gaussian noise per pixel per channel. | c |
| L351 | camera_gaussian_noise | +  | c |
| L352 | camera_gaussian_noise | +     Parameters | c |
| L353 | camera_gaussian_noise | +     ---------- | c |
| L354 | camera_gaussian_noise | +     sigma : float | c |
| L355 | camera_gaussian_noise | +         Noise std in 0–255 pixel-value units (default 10). | c |
| L356 | camera_gaussian_noise | +     """ | c |
| L357 | camera_gaussian_noise | +     sigma = params.get("sigma", 10.0) | c |
| L358 | camera_gaussian_noise | +     # Convert pixel-space sigma to normalized-tensor-space sigma | c |
| L359 | camera_gaussian_noise | +     sigma_norm = sigma / 255.0 / 0.229  # approximate — using mean std across channels | c |
| L360 | camera_gaussian_noise | +     for k in _camera_keys(dict_item): | c |
| L361 | camera_gaussian_noise | +         img = dict_item[k] | c |
| L362 | camera_gaussian_noise | +         noise = torch.randn_like(img) * sigma_norm | c |
| L363 | camera_gaussian_noise | +         dict_item[k] = img + noise | c |
| L364 | camera_gaussian_noise | +     return dict_item | c |
| L365 | camera_gaussian_noise | +  | c |
| L366 | camera_gaussian_noise | +  | c |
| L367 | camera_loss_partial | + def camera_loss_partial(dict_item: dict, params: dict, rng: np.random.Generator) -> dict: | c |
| L368 | camera_loss_partial | +     """C3 — Partial image data loss via single contiguous zeroed region. | c |
| L369 | camera_loss_partial | +  | c |
| L370 | camera_loss_partial | +     Zeros out a single rectangular region covering approximately ``fraction`` | c |
| L371 | camera_loss_partial | +     of the image area.  Region is randomly positioned. | c |
| L372 | camera_loss_partial | +  | c |
| L373 | camera_loss_partial | +     Distinct from multi-patch occlusion — this is the canonical "partial loss" | c |
| L374 | camera_loss_partial | +     corruption for images. | c |
| L375 | camera_loss_partial | +  | c |
| L376 | camera_loss_partial | +     Parameters | c |
| L377 | camera_loss_partial | +     ---------- | c |
| L378 | camera_loss_partial | +     fraction : float, optional | c |
| L379 | camera_loss_partial | +         Fraction of image area to zero out (default 0.2). | c |
| L380 | camera_loss_partial | +     """ | c |
| L381 | camera_loss_partial | +     fraction = params.get("fraction", 0.2) | c |
| L382 | camera_loss_partial | +     if fraction <= 0.0: | c |
| L383 | camera_loss_partial | +         return dict_item | c |
| L384 | camera_loss_partial | +     if fraction >= 1.0: | c |
| L385 | camera_loss_partial | +         # Complete blackout via the region mechanism; clip to 99% to avoid | c |
| L386 | camera_loss_partial | +         # degenerate region size. | c |
| L387 | camera_loss_partial | +         fraction = 0.99 | c |
| L388 | camera_loss_partial | +  | c |
| L389 | camera_loss_partial | +     for k in _camera_keys(dict_item): | c |
| L390 | camera_loss_partial | +         img_np = _to_nhwc(dict_item[k])  # (H, W, 3) uint8 | c |
| L391 | camera_loss_partial | +         H, W = img_np.shape[:2] | c |
| L392 | camera_loss_partial | +  | c |
| L393 | camera_loss_partial | +         # Region size: target_fraction = (ph * pw) / (H * W) | c |
| L394 | camera_loss_partial | +         # Fix aspect ratio ~1 (square-ish), compute side length | c |
| L395 | camera_loss_partial | +         target_area = fraction * H * W | c |
| L396 | camera_loss_partial | +         side = int(np.sqrt(target_area)) | c |
| L397 | camera_loss_partial | +         ph = min(max(1, side), H) | c |
| L398 | camera_loss_partial | +         pw = min(max(1, side), W) | c |
| L399 | camera_loss_partial | +         # Adjust to get as close as possible to target_area | c |
| L400 | camera_loss_partial | +         # Scale one dimension to hit area more closely | c |
| L401 | camera_loss_partial | +         if ph * pw > 0: | c |
| L402 | camera_loss_partial | +             ratio = np.clip(target_area / (ph * pw), 0.5, 2.0) | c |
| L403 | camera_loss_partial | +             if ratio >= 1.0: | c |
| L404 | camera_loss_partial | +                 pw = min(W, int(pw * np.sqrt(ratio))) | c |
| L405 | camera_loss_partial | +             else: | c |
| L406 | camera_loss_partial | +                 ph = min(H, int(ph / np.sqrt(ratio))) | c |
| L407 | camera_loss_partial | +  | c |
| L408 | camera_loss_partial | +         ph = max(1, min(ph, H)) | c |
| L409 | camera_loss_partial | +         pw = max(1, min(pw, W)) | c |
| L410 | camera_loss_partial | +  | c |
| L411 | camera_loss_partial | +         y0 = rng.integers(0, H - ph + 1) if H > ph else 0 | c |
| L412 | camera_loss_partial | +         x0 = rng.integers(0, W - pw + 1) if W > pw else 0 | c |
| L413 | camera_loss_partial | +  | c |
| L414 | camera_loss_partial | +         # Zero out the region | c |
| L415 | camera_loss_partial | +         img_np[y0: y0 + ph, x0: x0 + pw] = 0 | c |
| L416 | camera_loss_partial | +         dict_item[k] = _from_nhwc(img_np) | c |
| L417 | camera_loss_partial | +  | c |
| L418 | camera_loss_partial | +     return dict_item | c |
| L419 | camera_loss_partial | +  | c |
| L420 | camera_loss_partial | +  | c |
| L421 | camera_loss_complete | + def camera_loss_complete(dict_item: dict, params: dict, rng: np.random.Generator) -> dict: | c |
| L422 | camera_loss_complete | +     """C4 — Full image blackout. | c |
| L423 | camera_loss_complete | +  | c |
| L424 | camera_loss_complete | +     Replaces all camera-image tensors with zero-filled normalized tensors. | c |
| L425 | camera_loss_complete | +  | c |
| L426 | camera_loss_complete | +     Parameters: (none required) | c |
| L427 | camera_loss_complete | +     """ | c |
| L428 | camera_loss_complete | +     for k in _camera_keys(dict_item): | c |
| L429 | camera_loss_complete | +         dict_item[k] = _zero_camera_tensor(dict_item[k]) | c |
| L430 | camera_loss_complete | +     return dict_item | c |
| L431 | camera_loss_complete | +  | c |
| L432 | camera_loss_complete | +  | c |
| L433 | camera_loss_complete | + # ══════════════════════════════════════════════ | c |
| L434 | camera_loss_complete | + # NEW TAXONOMY REGISTRIES (Rev 2 — active) | c |
| L435 | camera_loss_complete | + # ══════════════════════════════════════════════ | c |
| L436 | camera_loss_complete | +  | c |
| L437 | camera_loss_complete | + RADAR_EFFECTS: dict[str, Callable] = { | c |
| L438 | camera_loss_complete | +     "frame_deletion":       radar_frame_deletion, | c |
| L439 | camera_loss_complete | +     "noise_induced_shifts": radar_noise_induced_shifts, | c |
| L440 | camera_loss_complete | +     "loss_partial":         radar_loss_partial, | c |
| L441 | camera_loss_complete | +     "loss_complete":        radar_loss_complete, | c |
| L442 | camera_loss_complete | + } | c |
| L443 | camera_loss_complete | +  | c |
| L444 | camera_loss_complete | + LIDAR_EFFECTS: dict[str, Callable] = { | c |
| L445 | camera_loss_complete | +     "frame_deletion":       lidar_frame_deletion, | c |
| L446 | camera_loss_complete | +     "gaussian_noise":       lidar_gaussian_noise, | c |
| L447 | camera_loss_complete | +     "loss_partial":         lidar_loss_partial, | c |
| L448 | camera_loss_complete | +     "loss_complete":        lidar_loss_complete, | c |
| L449 | camera_loss_complete | + } | c |
| L450 | camera_loss_complete | +  | c |
| L451 | camera_loss_complete | + CAMERA_EFFECTS: dict[str, Callable] = { | c |
| L452 | camera_loss_complete | +     "frame_deletion":       camera_frame_deletion, | c |
| L453 | camera_loss_complete | +     "gaussian_noise":       camera_gaussian_noise, | c |
| L454 | camera_loss_complete | +     "loss_partial":         camera_loss_partial, | c |
| L455 | camera_loss_complete | +     "loss_complete":        camera_loss_complete, | c |
| L456 | camera_loss_complete | + } | c |
| L457 | camera_loss_complete | +  | c |
| L458 | camera_loss_complete | + ALL_EFFECTS: dict[str, dict[str, Callable]] = { | c |
| L459 | camera_loss_complete | +     "radar":  RADAR_EFFECTS, | c |
| L460 | camera_loss_complete | +     "lidar":  LIDAR_EFFECTS, | c |
| L461 | camera_loss_complete | +     "camera": CAMERA_EFFECTS, | c |
| L462 | camera_loss_complete | + } | c |
| L463 | camera_loss_complete | +  | c |
| L464 | camera_loss_complete | + # Default ordering within each modality (recommended application order). | c |
| L465 | camera_loss_complete | + # Frame deletion first (empties sensor data; subsequent effects skip via _has_key). | c |
| L466 | camera_loss_complete | + # Loss complete should go last (it unconditionally blacks out; anything after is wasted). | c |
| L467 | camera_loss_complete | + DEFAULT_ORDER_RADAR = [ | c |
| L468 | camera_loss_complete | +     "frame_deletion",       # R1 — first, so other effects skip if frame gone | c |
| L469 | camera_loss_complete | +     "noise_induced_shifts", # R2 | c |
| L470 | camera_loss_complete | +     "loss_partial",         # R3 | c |
| L471 | camera_loss_complete | +     "loss_complete",        # R4 — last (unconditional blackout) | c |
| L472 | camera_loss_complete | + ] | c |
| L473 | camera_loss_complete | +  | c |
| L474 | camera_loss_complete | + DEFAULT_ORDER_LIDAR = [ | c |
| L475 | camera_loss_complete | +     "frame_deletion",       # L1 | c |
| L476 | camera_loss_complete | +     "gaussian_noise",       # L2 | c |
| L477 | camera_loss_complete | +     "loss_partial",         # L3 | c |
| L478 | camera_loss_complete | +     "loss_complete",        # L4 | c |
| L479 | camera_loss_complete | + ] | c |
| L480 | camera_loss_complete | +  | c |
| L481 | camera_loss_complete | + DEFAULT_ORDER_CAMERA = [ | c |
| L482 | camera_loss_complete | +     "frame_deletion",       # C1 | c |
| L483 | camera_loss_complete | +     "gaussian_noise",       # C2 | c |
| L484 | camera_loss_complete | +     "loss_partial",         # C3 | c |
| L485 | camera_loss_complete | +     "loss_complete",        # C4 | c |
| L486 | camera_loss_complete | + ] | c |
| L487 | camera_loss_complete | +  | c |
| L488 | camera_loss_complete | +  | c |
| L489 | camera_loss_complete | + # ══════════════════════════════════════════════ | c |
| L490 | camera_loss_complete | + # NoiseInjector class | c |
| L491 | camera_loss_complete | + # ══════════════════════════════════════════════ | c |
| L492 | camera_loss_complete | +  | c |
| L493 | camera_loss_complete | +  | c |
| L494 | camera_loss_complete | + class NoiseInjector: | c |
| L495 | camera_loss_complete | +     """Inference-time corruption module for K-Radar evaluation. | c |
| L496 | camera_loss_complete | +  | c |
| L497 | camera_loss_complete | +     Operates on post-__getitem__ dict_item.  Composable, probabilistic, | c |
| L498 | camera_loss_complete | +     seedable, and fully independent of the training pipeline. | c |
| L499 | camera_loss_complete | +  | c |
| L500 | camera_loss_complete | +     Usage:: | c |
| L501 | camera_loss_complete | +  | c |
| L502 | camera_loss_complete | +         injector = NoiseInjector(config) | c |
| L503 | camera_loss_complete | +         dict_item = injector(dict_item, frame_index=idx)  # after dataset[idx] | c |
| L504 | camera_loss_complete | +     """ | c |
| L505 | camera_loss_complete | +  | c |
| L506 | camera_loss_complete | +     def __init__(self, config: EffectConfig): | c |
| L507 | camera_loss_complete | +         self.config = config | c |
| L508 | camera_loss_complete | +         self.rng = np.random.default_rng(config.seed) | c |
| L509 | camera_loss_complete | +  | c |
| L510 | camera_loss_complete | +         # Resolve effect lists | c |
| L511 | camera_loss_complete | +         radar_effects = config.radar or [] | c |
| L512 | camera_loss_complete | +         lidar_effects = config.lidar or [] | c |
| L513 | camera_loss_complete | +         camera_effects = config.camera or [] | c |
| L514 | camera_loss_complete | +  | c |
| L515 | camera_loss_complete | +         self._radar_effects = self._resolve("radar", radar_effects) | c |
| L516 | camera_loss_complete | +         self._lidar_effects = self._resolve("lidar", lidar_effects) | c |
| L517 | camera_loss_complete | +         self._camera_effects = self._resolve("camera", camera_effects) | c |
| L518 | camera_loss_complete | +  | c |
| L519 | camera_loss_complete | +  | c |
| L524 | camera_loss_complete | +         }.get(modality, []) | c |
| L525 | camera_loss_complete | +         for name, fn, p, params, sub_rng in effect_list: | c |
| L526 | camera_loss_complete | +             if name == "frame_deletion" and sub_rng.uniform() < p: | c |
| L527 | camera_loss_complete | +                 # Deterministic check needs frame_index | c |
| L528 | camera_loss_complete | +                 if _frame_deletion_check(params, sub_rng, frame_index): | c |
| L529 | camera_loss_complete | +                     return True | c |
| L530 | camera_loss_complete | +         return False | c |
| L531 | camera_loss_complete | +  | c |
| L532 | camera_loss_complete | +     def _metadata(self) -> dict: | c |
| L533 | camera_loss_complete | +         """Return a summary of the current config for logging / audit.""" | c |
| L534 | camera_loss_complete | +         return { | c |
| L535 | camera_loss_complete | +             "seed": self.config.seed, | c |
| L536 | camera_loss_complete | +             "radar": [{"name": n, "p": p, "params": pr} for n, _, p, pr, _ in self._radar_effects], | c |
| L537 | camera_loss_complete | +             "lidar": [{"name": n, "p": p, "params": pr} for n, _, p, pr, _ in self._lidar_effects], | c |
| L538 | camera_loss_complete | +             "camera": [{"name": n, "p": p, "params": pr} for n, _, p, pr, _ in self._camera_effects], | c |
| L539 | camera_loss_complete | +         } | c |
| L46 | camera_loss_complete | - # RADAR EFFECTS  (R1–R7) | c |
| L543 | camera_loss_complete | + # LEGACY EFFECTS (Rev 1 — preserved for manual import) | c |
| L544 | camera_loss_complete | + # ══════════════════════════════════════════════ | c |
| L545 | camera_loss_complete | + # | c |
| L546 | camera_loss_complete | + # These are the 18 effects from the original design.  They are NOT loaded | c |
| L547 | camera_loss_complete | + # into ALL_EFFECTS and NOT used by NoiseInjector.  Code that directly | c |
| L548 | camera_loss_complete | + # imports them (e.g. individual function references in old test scripts) | c |
| L549 | camera_loss_complete | + # will still work, but they are not part of the active taxonomy. | c |
| L550 | camera_loss_complete | + # | c |
| L551 | camera_loss_complete | + # To use a legacy effect:: | c |
| L552 | camera_loss_complete | + #     from noise_injection import power_gaussian_noise | c |
| L553 | camera_loss_complete | + #     d = power_gaussian_noise(d, params, rng) | c |
| L556 | RADAR LEGACY (7 effects) | + # --- RADAR LEGACY (7 effects) --- | c |
| L50 | power_gaussian_noise | - def power_gaussian_noise(dict_item: dict, params: dict, rng: np.random.Generator) -> dict: | c |
| L51 | power_gaussian_noise | -     """R1 — Additive Gaussian noise to radar power values. | c |
| L52 | power_gaussian_noise | -  | c |
| L53 | power_gaussian_noise | -     Operates on ``rdr_sparse[:, 3]`` (power channel) and on | c |
| L54 | power_gaussian_noise | -     ``rdr_polar_3d[0]`` (power plane) if present. | c |
| L56 | power_gaussian_noise | -     Parameters | c |
| L57 | power_gaussian_noise | -     ---------- | c |
| L58 | power_gaussian_noise | -     std : float | c |
| L59 | power_gaussian_noise | -         Standard deviation of the additive Gaussian noise (in power units). | c |
| L60 | power_gaussian_noise | -     clip_min : float, optional | c |
| L61 | power_gaussian_noise | -         Floor value after adding noise (default: -inf). | c |
| L62 | power_gaussian_noise | -     """ | c |
| L559 | power_gaussian_noise | + def power_gaussian_noise(dict_item: dict, params: dict, rng: np.random.Generator) -> dict: | c |
| L560 | power_gaussian_noise | +     """[LEGACY] R1 — Additive Gaussian noise to radar power values.""" | c |
| L65 | power_gaussian_noise | -  | c |
| L84 | power_gaussian_noise | -     """R2 — Randomly drop rows from radar sparse point cloud. | c |
| L85 | power_gaussian_noise | -  | c |
| L86 | power_gaussian_noise | -     Parameters | c |
| L87 | power_gaussian_noise | -     ---------- | c |
| L88 | power_gaussian_noise | -     rate : float | c |
| L89 | power_gaussian_noise | -         Fraction of points to drop (0 = keep all, 1 = drop all). | c |
| L90 | power_gaussian_noise | -     """ | c |
| L660 | power_gaussian_noise | +     """[LEGACY] R2 — Randomly drop rows from radar sparse point cloud.""" | c |
| L104 | power_gaussian_noise | -     """R3 — Exponential range-based power attenuation. | c |
| L105 | power_gaussian_noise | -  | c |
| L106 | power_gaussian_noise | -     Scales power by ``exp(-alpha * max(r - r0, 0))`` where ``r`` is | c |
| L107 | power_gaussian_noise | -     Euclidean distance from origin. | c |
| L108 | power_gaussian_noise | -  | c |
| L109 | power_gaussian_noise | -     Parameters | c |
| L110 | power_gaussian_noise | -     ---------- | c |
| L111 | power_gaussian_noise | -     alpha : float | c |
| L112 | power_gaussian_noise | -         Attenuation coefficient (dB/m or neper/m  — applied as | c |
| L113 | power_gaussian_noise | -         ``exp(-alpha * dr)``). | c |
| L114 | power_gaussian_noise | -     r0 : float, optional | c |
| L115 | power_gaussian_noise | -         Start range in metres (default 0.0). | c |
| L116 | power_gaussian_noise | -     """ | c |
| L674 | power_gaussian_noise | +     """[LEGACY] R3 — Exponential range-based power attenuation.""" | c |
| L119 | power_gaussian_noise | -  | c |
| L135 | power_gaussian_noise | -     """R4 — Doppler channel corruption. | c |
| L136 | power_gaussian_noise | -  | c |
| L137 | power_gaussian_noise | -     Parameters | c |
| L138 | power_gaussian_noise | -     ---------- | c |
| L139 | power_gaussian_noise | -     mode : str | c |
| L140 | power_gaussian_noise | -         One of ``'gaussian'`` (add noise), ``'zero'`` (zero the channel), | c |
| L141 | power_gaussian_noise | -         ``'mask'`` (zero a random fraction of doppler bins). | c |
| L142 | power_gaussian_noise | -     std : float, optional | c |
| L143 | power_gaussian_noise | -         Gaussian noise sigma (only used when ``mode='gaussian'``). | c |
| L144 | power_gaussian_noise | -     mask_rate : float, optional | c |
| L145 | power_gaussian_noise | -         Fraction of bins to zero (only used when ``mode='mask'``). | c |
| L146 | power_gaussian_noise | -     """ | c |
| L692 | power_gaussian_noise | +     """[LEGACY] R4 — Doppler channel corruption.""" | c |
| L150 | power_gaussian_noise | -  | c |
| L151 | power_gaussian_noise | -     # rdr_polar_3d | c |
| L161 | power_gaussian_noise | -  | c |
| L162 | power_gaussian_noise | -     # pc100p has doppler at column 4 | c |
| L172 | power_gaussian_noise | -  | c |
| L177 | power_gaussian_noise | -     """R5 — Inject random false-positive radar points. | c |
| L178 | power_gaussian_noise | -  | c |
| L179 | power_gaussian_noise | -     Injects ``num`` new rows into ``rdr_sparse``. Positions are uniformly | c |
| L180 | power_gaussian_noise | -     sampled from the sensor FOV (default cube: [-50, 50] m per axis). | c |
| L181 | power_gaussian_noise | -     Power values are sampled from the observed power distribution of | c |
| L182 | power_gaussian_noise | -     existing points (or from a uniform distribution if no points exist). | c |
| L183 | power_gaussian_noise | -  | c |
| L184 | power_gaussian_noise | -     Parameters | c |
| L185 | power_gaussian_noise | -     ---------- | c |
| L186 | power_gaussian_noise | -     num : int | c |
| L187 | power_gaussian_noise | -         Number of ghost points to inject. | c |
| L188 | power_gaussian_noise | -     x_range : tuple[float, float], optional | c |
| L189 | power_gaussian_noise | -         X-axis bounds (default (-50, 50)). | c |
| L190 | power_gaussian_noise | -     y_range : tuple[float, float], optional | c |
| L191 | power_gaussian_noise | -         Y-axis bounds (default (-50, 50)). | c |
| L192 | power_gaussian_noise | -     z_range : tuple[float, float], optional | c |
| L193 | power_gaussian_noise | -         Z-axis bounds (default (-3, 5)). | c |
| L194 | power_gaussian_noise | -     power_bounds : tuple[float, float], optional | c |
| L195 | power_gaussian_noise | -         Power range for ghost points (min, max) when no reference exists. | c |
| L196 | power_gaussian_noise | -     """ | c |
| L718 | power_gaussian_noise | +     """[LEGACY] R5 — Inject random false-positive radar points.""" | c |
| L202 | power_gaussian_noise | -  | c |
| L212 | power_gaussian_noise | -                 # Sample from observed power distribution | c |
| L217 | power_gaussian_noise | -             # Copy doppler from existing if available | c |
| L227 | power_gaussian_noise | -     """R6 — Angular jitter on radar point positions. | c |
| L228 | power_gaussian_noise | -  | c |
| L229 | power_gaussian_noise | -     Perturbs each point's azimuth around the sensor origin with | c |
| L230 | power_gaussian_noise | -     ``N(0, sigma_deg)`` degrees. | c |
| L231 | power_gaussian_noise | -  | c |
| L232 | power_gaussian_noise | -     Parameters | c |
| L233 | power_gaussian_noise | -     ---------- | c |
| L234 | power_gaussian_noise | -     sigma_deg : float | c |
| L235 | power_gaussian_noise | -         Standard deviation of angular jitter in degrees. | c |
| L236 | power_gaussian_noise | -     per_axis : bool, optional | c |
| L237 | power_gaussian_noise | -         If True, apply independent jitter to azimuth and elevation | c |
| L238 | power_gaussian_noise | -         (default False, jitter only azimuth). | c |
| L239 | power_gaussian_noise | -     """ | c |
| L746 | power_gaussian_noise | +     """[LEGACY] R6 — Angular jitter on radar point positions.""" | c |
| L243 | power_gaussian_noise | -  | c |
| L250 | power_gaussian_noise | -  | c |
| L254 | power_gaussian_noise | -  | c |
| L262 | power_gaussian_noise | -     """R7 — Clamp radar power values to a ceiling. | c |
| L263 | power_gaussian_noise | -  | c |
| L264 | power_gaussian_noise | -     Parameters | c |
| L265 | power_gaussian_noise | -     ---------- | c |
| L266 | power_gaussian_noise | -     ceiling : float | c |
| L267 | power_gaussian_noise | -         Maximum allowed power value. | c |
| L268 | power_gaussian_noise | -     floor : float, optional | c |
| L269 | power_gaussian_noise | -         Minimum allowed power value (default -inf). | c |
| L270 | power_gaussian_noise | -     """ | c |
| L766 | power_gaussian_noise | +     """[LEGACY] R7 — Clamp radar power values to a ceiling.""" | c |
| L273 | power_gaussian_noise | -  | c |
| L283 | power_gaussian_noise | - # ══════════════════════════════════════════════ | c |
| L284 | power_gaussian_noise | - # LIDAR EFFECTS  (L1–L5) | c |
| L285 | power_gaussian_noise | - # ══════════════════════════════════════════════ | c |
| L778 | LIDAR LEGACY (5 effects) | + # --- LIDAR LEGACY (5 effects) --- | c |
| L289 | LIDAR LEGACY (5 effects) | -     """L1 — Uniform-random dropout of LiDAR points. | c |
| L290 | LIDAR LEGACY (5 effects) | -  | c |
| L291 | LIDAR LEGACY (5 effects) | -     Parameters | c |
| L292 | LIDAR LEGACY (5 effects) | -     ---------- | c |
| L293 | LIDAR LEGACY (5 effects) | -     rate : float | c |
| L294 | LIDAR LEGACY (5 effects) | -         Fraction of points to drop (0 = keep all, 1 = drop all). | c |
| L295 | LIDAR LEGACY (5 effects) | -     """ | c |
| L782 | LIDAR LEGACY (5 effects) | +     """[LEGACY] L1 — Uniform-random dropout of LiDAR points.""" | c |
| L305 | LIDAR LEGACY (5 effects) | -     """L2 — FOV occlusion by azimuth sector. | c |
| L306 | LIDAR LEGACY (5 effects) | -  | c |
| L307 | LIDAR LEGACY (5 effects) | -     Keeps only points whose azimuth is **outside** ``[min_deg, max_deg]`` | c |
| L308 | LIDAR LEGACY (5 effects) | -     (or **inside** if ``invert=True``). | c |
| L309 | LIDAR LEGACY (5 effects) | -  | c |
| L310 | LIDAR LEGACY (5 effects) | -     Parameters | c |
| L311 | LIDAR LEGACY (5 effects) | -     ---------- | c |
| L312 | LIDAR LEGACY (5 effects) | -     min_deg : float | c |
| L313 | LIDAR LEGACY (5 effects) | -         Start of occluded sector in degrees. | c |
| L314 | LIDAR LEGACY (5 effects) | -     max_deg : float | c |
| L315 | LIDAR LEGACY (5 effects) | -         End of occluded sector in degrees. | c |
| L316 | LIDAR LEGACY (5 effects) | -     invert : bool, optional | c |
| L317 | LIDAR LEGACY (5 effects) | -         If True, keep points *inside* the sector instead (default False). | c |
| L318 | LIDAR LEGACY (5 effects) | -     """ | c |
| L792 | LIDAR LEGACY (5 effects) | +     """[LEGACY] L2 — FOV occlusion by azimuth sector.""" | c |
| L322 | LIDAR LEGACY (5 effects) | -  | c |
| L325 | LIDAR LEGACY (5 effects) | -         az = np.arctan2(pc[:, 1], pc[:, 0])  # radians in [-pi, pi] | c |
| L798 | LIDAR LEGACY (5 effects) | +         az = np.arctan2(pc[:, 1], pc[:, 0]) | c |
| L327 | LIDAR LEGACY (5 effects) | -  | c |
| L329 | LIDAR LEGACY (5 effects) | -             # Keep points inside the sector | c |
| L332 | LIDAR LEGACY (5 effects) | -             # Keep points outside the sector (original K-Radar behaviour) | c |
| L339 | LIDAR LEGACY (5 effects) | -     """L3 — Additive Gaussian noise to LiDAR (x, y, z) positions. | c |
| L340 | LIDAR LEGACY (5 effects) | -  | c |
| L341 | LIDAR LEGACY (5 effects) | -     Parameters | c |
| L342 | LIDAR LEGACY (5 effects) | -     ---------- | c |
| L343 | LIDAR LEGACY (5 effects) | -     sigma_xy : float | c |
| L344 | LIDAR LEGACY (5 effects) | -         Std dev of noise in x and y (metres). | c |
| L345 | LIDAR LEGACY (5 effects) | -     sigma_z : float, optional | c |
| L346 | LIDAR LEGACY (5 effects) | -         Std dev of noise in z (metres), defaults to sigma_xy. | c |
| L347 | LIDAR LEGACY (5 effects) | -     """ | c |
| L809 | LIDAR LEGACY (5 effects) | +     """[LEGACY] L3 — Additive Gaussian noise to LiDAR positions only.""" | c |
| L350 | LIDAR LEGACY (5 effects) | -  | c |
| L362 | LIDAR LEGACY (5 effects) | -     """L4 — Drop LiDAR points outside a specified range interval. | c |
| L363 | LIDAR LEGACY (5 effects) | -  | c |
| L364 | LIDAR LEGACY (5 effects) | -     Parameters | c |
| L365 | LIDAR LEGACY (5 effects) | -     ---------- | c |
| L366 | LIDAR LEGACY (5 effects) | -     r_min : float, optional | c |
| L367 | LIDAR LEGACY (5 effects) | -         Minimum range in metres (default 0.0). | c |
| L368 | LIDAR LEGACY (5 effects) | -     r_max : float, optional | c |
| L369 | LIDAR LEGACY (5 effects) | -         Maximum range in metres (default 200.0). | c |
| L370 | LIDAR LEGACY (5 effects) | -     """ | c |
| L823 | LIDAR LEGACY (5 effects) | +     """[LEGACY] L4 — Drop LiDAR points outside a specified range interval.""" | c |
| L373 | LIDAR LEGACY (5 effects) | -  | c |
| L383 | LIDAR LEGACY (5 effects) | -     """L5 — Uniform-stride downsampling of LiDAR point cloud. | c |
| L384 | LIDAR LEGACY (5 effects) | -  | c |
| L385 | LIDAR LEGACY (5 effects) | -     Parameters | c |
| L386 | LIDAR LEGACY (5 effects) | -     ---------- | c |
| L387 | LIDAR LEGACY (5 effects) | -     stride : int | c |
| L388 | LIDAR LEGACY (5 effects) | -         Keep every Nth point (stride of 4 keeps 1/4 of points). | c |
| L389 | LIDAR LEGACY (5 effects) | -     """ | c |
| L835 | LIDAR LEGACY (5 effects) | +     """[LEGACY] L5 — Uniform-stride downsampling of LiDAR point cloud.""" | c |
| L396 | LIDAR LEGACY (5 effects) | - # ══════════════════════════════════════════════ | c |
| L397 | LIDAR LEGACY (5 effects) | - # CAMERA EFFECTS  (C1–C6) | c |
| L398 | LIDAR LEGACY (5 effects) | - # ══════════════════════════════════════════════ | c |
| L399 | LIDAR LEGACY (5 effects) | -  | c |
| L400 | LIDAR LEGACY (5 effects) | - # Camera helper: find all camera-image keys in the dict_item. | c |
| L401 | LIDAR LEGACY (5 effects) | - # These are the keys from dset.list_dealt_cams (e.g. front0, front1, ...) | c |
| L402 | LIDAR LEGACY (5 effects) | - # stored as (3, H, W) torch.Tensor (ToTensor + Normalize). | c |
| L403 | LIDAR LEGACY (5 effects) | -  | c |
| L404 | LIDAR LEGACY (5 effects) | -  | c |
| L405 | _camera_keys | - def _camera_keys(d: dict) -> list[str]: | c |
| L406 | _camera_keys | -     """Return camera-image keys in the dict_item (batched torch.Tensor).""" | c |
| L407 | _camera_keys | -     known = {"front0", "front1", "left0", "left1", "right0", "right1", "rear0", "rear1"} | c |
| L408 | _camera_keys | -     return [k for k in known if k in d and isinstance(d[k], torch.Tensor)] | c |
| L409 | _camera_keys | -  | c |
| L410 | _camera_keys | -  | c |
| L411 | _to_nhwc | - def _to_nhwc(img: torch.Tensor) -> np.ndarray: | c |
| L412 | _to_nhwc | -     """Convert (3, H, W) normalized torch.Tensor → (H, W, 3) uint8 numpy.""" | c |
| L413 | _to_nhwc | -     # Undo ImageNet-style normalization approximately: clamp to reasonable range | c |
| L414 | _to_nhwc | -     # then rescale [0,1] → uint8 | c |
| L415 | _to_nhwc | -     img_np = img.cpu().numpy().transpose(1, 2, 0)  # (H, W, 3) | c |
| L416 | _to_nhwc | -     # Simple de-normalize: shift + scale to [0,1] | c |
| L417 | _to_nhwc | -     mean = np.array([0.485, 0.456, 0.406], dtype=np.float32) | c |
| L418 | _to_nhwc | -     std = np.array([0.229, 0.224, 0.225], dtype=np.float32) | c |
| L419 | _to_nhwc | -     img_np = img_np * std + mean | c |
| L420 | _to_nhwc | -     img_np = np.clip(img_np * 255.0, 0, 255).astype(np.uint8) | c |
| L421 | _to_nhwc | -     return img_np | c |
| L422 | _to_nhwc | -  | c |
| L423 | _to_nhwc | -  | c |
| L424 | _from_nhwc | - def _from_nhwc(arr: np.ndarray) -> torch.Tensor: | c |
| L425 | _from_nhwc | -     """Convert (H, W, 3) uint8 numpy → (3, H, W) normalized torch.Tensor.""" | c |
| L426 | _from_nhwc | -     img_f = arr.astype(np.float32) / 255.0 | c |
| L427 | _from_nhwc | -     mean = np.array([0.485, 0.456, 0.406], dtype=np.float32) | c |
| L428 | _from_nhwc | -     std = np.array([0.229, 0.224, 0.225], dtype=np.float32) | c |
| L429 | _from_nhwc | -     img_f = (img_f - mean) / std | c |
| L430 | _from_nhwc | -     return torch.from_numpy(img_f.transpose(2, 0, 1)) | c |
| L431 | _from_nhwc | -  | c |
| L432 | _from_nhwc | -  | c |
| L433 | camera_gaussian_noise | - def camera_gaussian_noise(dict_item: dict, params: dict, rng: np.random.Generator) -> dict: | c |
| L434 | camera_gaussian_noise | -     """C1 — Additive Gaussian noise per pixel per channel. | c |
| L435 | camera_gaussian_noise | -  | c |
| L436 | camera_gaussian_noise | -     Parameters | c |
| L437 | camera_gaussian_noise | -     ---------- | c |
| L438 | camera_gaussian_noise | -     sigma : float | c |
| L439 | camera_gaussian_noise | -         Noise std in 0–255 pixel-value units (default 10). | c |
| L440 | camera_gaussian_noise | -     """ | c |
| L441 | camera_gaussian_noise | -     sigma = params.get("sigma", 10.0) | c |
| L442 | camera_gaussian_noise | -     # Convert pixel-space sigma to normalized-tensor-space sigma | c |
| L443 | camera_gaussian_noise | -     sigma_norm = sigma / 255.0 / 0.229  # approximate — using mean std across channels | c |
| L444 | camera_gaussian_noise | -     for k in _camera_keys(dict_item): | c |
| L445 | camera_gaussian_noise | -         img = dict_item[k] | c |
| L446 | camera_gaussian_noise | -         noise = torch.randn_like(img) * sigma_norm | c |
| L447 | camera_gaussian_noise | -         dict_item[k] = img + noise | c |
| L448 | camera_gaussian_noise | -     return dict_item | c |
| L842 | CAMERA LEGACY (6 effects) | + # --- CAMERA LEGACY (6 effects) --- | c |
| L452 | CAMERA LEGACY (6 effects) | -     """C2 — Directional motion blur via OpenCV filter2D. | c |
| L453 | CAMERA LEGACY (6 effects) | -  | c |
| L454 | CAMERA LEGACY (6 effects) | -     Parameters | c |
| L455 | CAMERA LEGACY (6 effects) | -     ---------- | c |
| L456 | CAMERA LEGACY (6 effects) | -     kernel_size : int | c |
| L457 | CAMERA LEGACY (6 effects) | -         Odd-sized kernel (e.g. 5, 9). Larger = more blur. | c |
| L458 | CAMERA LEGACY (6 effects) | -     angle_deg : float | c |
| L459 | CAMERA LEGACY (6 effects) | -         Blur direction in degrees (0 = horizontal right). | c |
| L460 | CAMERA LEGACY (6 effects) | -     intensity : float, optional | c |
| L461 | CAMERA LEGACY (6 effects) | -         Blur weight; 1.0 = full kernel, <1 = blend with original (default 1.0). | c |
| L462 | CAMERA LEGACY (6 effects) | -     """ | c |
| L846 | CAMERA LEGACY (6 effects) | +     """[LEGACY] C2 — Directional motion blur via OpenCV filter2D.""" | c |
| L466 | CAMERA LEGACY (6 effects) | -     ksize = ksize if ksize % 2 == 1 else ksize + 1  # enforce odd | c |
| L467 | CAMERA LEGACY (6 effects) | -  | c |
| L850 | CAMERA LEGACY (6 effects) | +     ksize = ksize if ksize % 2 == 1 else ksize + 1 | c |
| L473 | CAMERA LEGACY (6 effects) | -         dx = c  # fallback to horizontal when angle is axis-aligned | c |
| L856 | CAMERA LEGACY (6 effects) | +         dx = c | c |
| L476 | CAMERA LEGACY (6 effects) | -  | c |
| L487 | CAMERA LEGACY (6 effects) | -     """C3 — Brightness adjustment by multiplicative factor. | c |
| L488 | CAMERA LEGACY (6 effects) | -  | c |
| L489 | CAMERA LEGACY (6 effects) | -     Parameters | c |
| L490 | CAMERA LEGACY (6 effects) | -     ---------- | c |
| L491 | CAMERA LEGACY (6 effects) | -     factor : float | c |
| L492 | CAMERA LEGACY (6 effects) | -         Multiplier applied to all pixel values (before clipping to [0,1]). | c |
| L493 | CAMERA LEGACY (6 effects) | -     """ | c |
| L869 | CAMERA LEGACY (6 effects) | +     """[LEGACY] C3 — Brightness adjustment by multiplicative factor.""" | c |
| L497 | CAMERA LEGACY (6 effects) | -         # De-normalize to [0,1], multiply, re-normalize | c |
| L500 | CAMERA LEGACY (6 effects) | -         img_pixel = img * std + mean  # [0, 1] approx | c |
| L875 | CAMERA LEGACY (6 effects) | +         img_pixel = img * std + mean | c |
| L507 | CAMERA LEGACY (6 effects) | -     """C4 — Random rectangular patch occlusion. | c |
| L508 | CAMERA LEGACY (6 effects) | -  | c |
| L509 | CAMERA LEGACY (6 effects) | -     Parameters | c |
| L510 | CAMERA LEGACY (6 effects) | -     ---------- | c |
| L511 | CAMERA LEGACY (6 effects) | -     num_patches : int | c |
| L512 | CAMERA LEGACY (6 effects) | -         Number of patches to draw (default 3). | c |
| L513 | CAMERA LEGACY (6 effects) | -     max_size_h : float, optional | c |
| L514 | CAMERA LEGACY (6 effects) | -         Max patch height as fraction of image height (default 0.15). | c |
| L515 | CAMERA LEGACY (6 effects) | -     max_size_w : float, optional | c |
| L516 | CAMERA LEGACY (6 effects) | -         Max patch width as fraction of image width (default 0.15). | c |
| L517 | CAMERA LEGACY (6 effects) | -     fill : str, optional | c |
| L518 | CAMERA LEGACY (6 effects) | -         Fill type: ``'black'``, ``'white'``, ``'mean'``, or ``'random'`` | c |
| L519 | CAMERA LEGACY (6 effects) | -         (default ``'black'``). | c |
| L520 | CAMERA LEGACY (6 effects) | -     """ | c |
| L882 | CAMERA LEGACY (6 effects) | +     """[LEGACY] C4 — Random rectangular patch occlusion.""" | c |
| L525 | CAMERA LEGACY (6 effects) | -  | c |
| L527 | CAMERA LEGACY (6 effects) | -         img_np = _to_nhwc(dict_item[k])  # (H, W, 3) uint8 | c |
| L888 | CAMERA LEGACY (6 effects) | +         img_np = _to_nhwc(dict_item[k]) | c |
| L535 | CAMERA LEGACY (6 effects) | -                 img_np[y0 : y0 + ph, x0 : x0 + pw] = 0 | c |
| L896 | CAMERA LEGACY (6 effects) | +                 img_np[y0: y0 + ph, x0: x0 + pw] = 0 | c |
| L537 | CAMERA LEGACY (6 effects) | -                 img_np[y0 : y0 + ph, x0 : x0 + pw] = 255 | c |
| L898 | CAMERA LEGACY (6 effects) | +                 img_np[y0: y0 + ph, x0: x0 + pw] = 255 | c |
| L539 | CAMERA LEGACY (6 effects) | -                 patch_mean = img_np[y0 : y0 + ph, x0 : x0 + pw].mean(axis=(0, 1), keepdims=True).astype(np.uint8) | c |
| L540 | CAMERA LEGACY (6 effects) | -                 img_np[y0 : y0 + ph, x0 : x0 + pw] = patch_mean | c |
| L900 | CAMERA LEGACY (6 effects) | +                 patch_mean = img_np[y0: y0 + ph, x0: x0 + pw].mean(axis=(0, 1), keepdims=True).astype(np.uint8) | c |
| L901 | CAMERA LEGACY (6 effects) | +                 img_np[y0: y0 + ph, x0: x0 + pw] = patch_mean | c |
| L543 | CAMERA LEGACY (6 effects) | -                 img_np[y0 : y0 + ph, x0 : x0 + pw] = rand_color.reshape(1, 1, 3) | c |
| L904 | CAMERA LEGACY (6 effects) | +                 img_np[y0: y0 + ph, x0: x0 + pw] = rand_color.reshape(1, 1, 3) | c |
| L549 | CAMERA LEGACY (6 effects) | -     """C5 — JPEG compression/decompression at a given quality level. | c |
| L550 | CAMERA LEGACY (6 effects) | -  | c |
| L551 | CAMERA LEGACY (6 effects) | -     Parameters | c |
| L552 | CAMERA LEGACY (6 effects) | -     ---------- | c |
| L553 | CAMERA LEGACY (6 effects) | -     quality : int | c |
| L554 | CAMERA LEGACY (6 effects) | -         JPEG quality 1–100 (lower = more artifacts, default 50). | c |
| L555 | CAMERA LEGACY (6 effects) | -     """ | c |
| L910 | CAMERA LEGACY (6 effects) | +     """[LEGACY] C5 — JPEG compression/decompression at a given quality level.""" | c |
| L558 | CAMERA LEGACY (6 effects) | -  | c |
| L569 | CAMERA LEGACY (6 effects) | -     """C6 — Gamma (power-law) distortion. | c |
| L570 | CAMERA LEGACY (6 effects) | -  | c |
| L571 | CAMERA LEGACY (6 effects) | -     Parameters | c |
| L572 | CAMERA LEGACY (6 effects) | -     ---------- | c |
| L573 | CAMERA LEGACY (6 effects) | -     gamma : float | c |
| L574 | CAMERA LEGACY (6 effects) | -         Gamma value (typical 0.5–2.0). <1 brightens, >1 darkens. | c |
| L575 | CAMERA LEGACY (6 effects) | -     """ | c |
| L923 | CAMERA LEGACY (6 effects) | +     """[LEGACY] C6 — Gamma (power-law) distortion.""" | c |
| L578 | CAMERA LEGACY (6 effects) | -  | c |
| L580 | CAMERA LEGACY (6 effects) | -         img_np = _to_nhwc(dict_item[k])  # (H, W, 3) uint8 | c |
| L581 | CAMERA LEGACY (6 effects) | -         # Apply gamma to uint8 via LUT | c |
| L927 | CAMERA LEGACY (6 effects) | +         img_np = _to_nhwc(dict_item[k]) | c |
| L589 | CAMERA LEGACY (6 effects) | - # ══════════════════════════════════════════════ | c |
| L590 | CAMERA LEGACY (6 effects) | - # EFFECT REGISTRIES | c |
| L591 | CAMERA LEGACY (6 effects) | - # ══════════════════════════════════════════════ | c |
| L935 | LEGACY REGISTRIES | + # --- LEGACY REGISTRIES --- | c |
| L593 | LEGACY REGISTRIES | - RADAR_EFFECTS: dict[str, Callable] = { | c |
| L594 | LEGACY REGISTRIES | -     "power_gaussian_noise": power_gaussian_noise, | c |
| L595 | LEGACY REGISTRIES | -     "sparse_point_dropout": sparse_point_dropout, | c |
| L596 | LEGACY REGISTRIES | -     "range_attenuation": range_attenuation, | c |
| L597 | LEGACY REGISTRIES | -     "doppler_corruption": doppler_corruption, | c |
| L598 | LEGACY REGISTRIES | -     "ghost_points": ghost_points, | c |
| L599 | LEGACY REGISTRIES | -     "azimuth_jitter": azimuth_jitter, | c |
| L600 | LEGACY REGISTRIES | -     "power_saturation": power_saturation, | c |
| L937 | LEGACY REGISTRIES | + RADAR_EFFECTS_LEGACY: dict[str, Callable] = { | c |
| L938 | LEGACY REGISTRIES | +     "power_gaussian_noise":     power_gaussian_noise, | c |
| L939 | LEGACY REGISTRIES | +     "sparse_point_dropout":     sparse_point_dropout, | c |
| L940 | LEGACY REGISTRIES | +     "range_attenuation":        range_attenuation, | c |
| L941 | LEGACY REGISTRIES | +     "doppler_corruption":       doppler_corruption, | c |
| L942 | LEGACY REGISTRIES | +     "ghost_points":             ghost_points, | c |
| L943 | LEGACY REGISTRIES | +     "azimuth_jitter":           azimuth_jitter, | c |
| L944 | LEGACY REGISTRIES | +     "power_saturation":         power_saturation, | c |
| L603 | LEGACY REGISTRIES | - LIDAR_EFFECTS: dict[str, Callable] = { | c |
| L604 | LEGACY REGISTRIES | -     "random_dropout": lidar_random_dropout, | c |
| L605 | LEGACY REGISTRIES | -     "fov_occlusion": lidar_fov_occlusion, | c |
| L606 | LEGACY REGISTRIES | -     "position_noise": lidar_position_noise, | c |
| L607 | LEGACY REGISTRIES | -     "range_dropout": lidar_range_dropout, | c |
| L608 | LEGACY REGISTRIES | -     "downsampling": lidar_downsampling, | c |
| L947 | LEGACY REGISTRIES | + LIDAR_EFFECTS_LEGACY: dict[str, Callable] = { | c |
| L948 | LEGACY REGISTRIES | +     "random_dropout":   lidar_random_dropout, | c |
| L949 | LEGACY REGISTRIES | +     "fov_occlusion":    lidar_fov_occlusion, | c |
| L950 | LEGACY REGISTRIES | +     "position_noise":   lidar_position_noise, | c |
| L951 | LEGACY REGISTRIES | +     "range_dropout":    lidar_range_dropout, | c |
| L952 | LEGACY REGISTRIES | +     "downsampling":     lidar_downsampling, | c |
| L611 | LEGACY REGISTRIES | - CAMERA_EFFECTS: dict[str, Callable] = { | c |
| L612 | LEGACY REGISTRIES | -     "gaussian_noise": camera_gaussian_noise, | c |
| L613 | LEGACY REGISTRIES | -     "motion_blur": camera_motion_blur, | c |
| L614 | LEGACY REGISTRIES | -     "brightness": camera_brightness, | c |
| L615 | LEGACY REGISTRIES | -     "patch_occlusion": camera_patch_occlusion, | c |
| L955 | LEGACY REGISTRIES | + CAMERA_EFFECTS_LEGACY: dict[str, Callable] = { | c |
| L956 | LEGACY REGISTRIES | +     # NOTE: camera_gaussian_noise is NOT listed here. It was carried forward | c |
| L957 | LEGACY REGISTRIES | +     # into the active CAMERA_EFFECTS registry without changes — the new-taxonomy | c |
| L958 | LEGACY REGISTRIES | +     # function IS the canonical version there is no separate legacy copy. | c |
| L959 | LEGACY REGISTRIES | +     # Accessible via CAMERA_EFFECTS["gaussian_noise"] or by importing | c |
| L960 | LEGACY REGISTRIES | +     # camera_gaussian_noise directly at module level. | c |
| L961 | LEGACY REGISTRIES | +     "motion_blur":      camera_motion_blur, | c |
| L962 | LEGACY REGISTRIES | +     "brightness":       camera_brightness, | c |
| L963 | LEGACY REGISTRIES | +     "patch_occlusion":  camera_patch_occlusion, | c |
| L620 | LEGACY REGISTRIES | - ALL_EFFECTS: dict[str, dict[str, Callable]] = { | c |
| L621 | LEGACY REGISTRIES | -     "radar": RADAR_EFFECTS, | c |
| L622 | LEGACY REGISTRIES | -     "lidar": LIDAR_EFFECTS, | c |
| L623 | LEGACY REGISTRIES | -     "camera": CAMERA_EFFECTS, | c |
| L624 | LEGACY REGISTRIES | - } | c |
| L625 | LEGACY REGISTRIES | -  | c |
| L626 | LEGACY REGISTRIES | - # Default ordering within each modality (recommended application order). | c |
| L627 | LEGACY REGISTRIES | - # Applied in list order; reorder by passing effects in the desired order. | c |
| L628 | LEGACY REGISTRIES | - DEFAULT_ORDER_RADAR = [ | c |
| L629 | LEGACY REGISTRIES | -     "azimuth_jitter",          # R6 | c |
| L630 | LEGACY REGISTRIES | -     "power_saturation",        # R7 | c |
| L631 | LEGACY REGISTRIES | -     "power_gaussian_noise",    # R1 | c |
| L632 | LEGACY REGISTRIES | -     "doppler_corruption",      # R4 | c |
| L633 | LEGACY REGISTRIES | -     "range_attenuation",       # R3 | c |
| L634 | LEGACY REGISTRIES | -     "sparse_point_dropout",    # R2 | c |
| L635 | LEGACY REGISTRIES | -     "ghost_points",            # R5 | c |
| L636 | LEGACY REGISTRIES | - ] | c |
| L637 | LEGACY REGISTRIES | -  | c |
| L638 | LEGACY REGISTRIES | - DEFAULT_ORDER_LIDAR = [ | c |
| L639 | LEGACY REGISTRIES | -     "range_dropout",           # L4 | c |
| L640 | LEGACY REGISTRIES | -     "fov_occlusion",           # L2 | c |
| L641 | LEGACY REGISTRIES | -     "position_noise",          # L3 | c |
| L642 | LEGACY REGISTRIES | -     "random_dropout",          # L1 | c |
| L643 | LEGACY REGISTRIES | -     "downsampling",            # L5 | c |
| L644 | LEGACY REGISTRIES | - ] | c |
| L645 | LEGACY REGISTRIES | -  | c |
| L646 | LEGACY REGISTRIES | - DEFAULT_ORDER_CAMERA = [ | c |
| L647 | LEGACY REGISTRIES | -     "brightness",              # C3 | c |
| L648 | LEGACY REGISTRIES | -     "gamma_distortion",        # C6 | c |
| L649 | LEGACY REGISTRIES | -     "gaussian_noise",          # C1 | c |
| L650 | LEGACY REGISTRIES | -     "motion_blur",             # C2 | c |
| L651 | LEGACY REGISTRIES | -     "patch_occlusion",         # C4 | c |
| L652 | LEGACY REGISTRIES | -     "jpeg_compression",        # C5 | c |
| L653 | LEGACY REGISTRIES | - ] | c |
| L654 | LEGACY REGISTRIES | -  | c |
| L655 | LEGACY REGISTRIES | -  | c |
| L656 | LEGACY REGISTRIES | - # ══════════════════════════════════════════════ | c |
| L657 | LEGACY REGISTRIES | - # NoiseInjector class | c |
| L658 | LEGACY REGISTRIES | - # ══════════════════════════════════════════════ | c |
| L659 | LEGACY REGISTRIES | -  | c |
| L660 | LEGACY REGISTRIES | -  | c |
| L661 | LEGACY REGISTRIES | - class NoiseInjector: | c |
| L662 | LEGACY REGISTRIES | -     """Inference-time corruption module for K-Radar evaluation. | c |
| L663 | LEGACY REGISTRIES | -  | c |
| L664 | LEGACY REGISTRIES | -     Operates on post-__getitem__ dict_item.  Composable, probabilistic, | c |
| L665 | LEGACY REGISTRIES | -     seedable, and fully independent of the training pipeline. | c |
| L666 | LEGACY REGISTRIES | -  | c |
| L667 | LEGACY REGISTRIES | -     Usage:: | c |
| L668 | LEGACY REGISTRIES | -  | c |
| L669 | LEGACY REGISTRIES | -         injector = NoiseInjector(config) | c |
| L670 | LEGACY REGISTRIES | -         dict_item = injector(dict_item)   # after dataset[idx_frame] | c |
| L671 | LEGACY REGISTRIES | -     """ | c |
| L672 | LEGACY REGISTRIES | -  | c |
| L673 | LEGACY REGISTRIES | -     def __init__(self, config: EffectConfig): | c |
| L674 | LEGACY REGISTRIES | -         self.config = config | c |
| L675 | LEGACY REGISTRIES | -         self.rng = np.random.default_rng(config.seed) | c |
| L676 | LEGACY REGISTRIES | -  | c |
| L677 | LEGACY REGISTRIES | -         # Resolve effect lists — use default ordering if no explicit order given | c |
| L678 | LEGACY REGISTRIES | -         radar_effects = config.radar or [] | c |
| L679 | LEGACY REGISTRIES | -         lidar_effects = config.lidar or [] | c |
| L680 | LEGACY REGISTRIES | -         camera_effects = config.camera or [] | c |
| L681 | LEGACY REGISTRIES | -  | c |
| L682 | LEGACY REGISTRIES | -         self._radar_effects = self._resolve("radar", radar_effects) | c |
| L683 | LEGACY REGISTRIES | -         self._lidar_effects = self._resolve("lidar", lidar_effects) | c |
| L684 | LEGACY REGISTRIES | -         self._camera_effects = self._resolve("camera", camera_effects) | c |
| L685 | LEGACY REGISTRIES | -  | c |
| L686 | LEGACY REGISTRIES | -     def _resolve( | c |
| L687 | LEGACY REGISTRIES | -         self, modality: str, user_effects: list[Any] | c |
| L688 | LEGACY REGISTRIES | -     ) -> list[tuple[str, Callable, float, dict, np.random.Generator]]: | c |
| L689 | LEGACY REGISTRIES | -         """Resolve (name, fn, p, params, sub_rng) for each configured effect.""" | c |
| L690 | LEGACY REGISTRIES | -         registry = ALL_EFFECTS[modality] | c |
| L691 | LEGACY REGISTRIES | -         resolved: list[tuple[str, Callable, float, dict, np.random.Generator]] = [] | c |
| L692 | LEGACY REGISTRIES | -         for i, eff in enumerate(user_effects): | c |
| L693 | LEGACY REGISTRIES | -             name = eff.name if hasattr(eff, "name") else eff["name"] | c |
| L694 | LEGACY REGISTRIES | -             p = eff.p if hasattr(eff, "p") else eff.get("p", 1.0) | c |
| L695 | LEGACY REGISTRIES | -             params = eff.params if hasattr(eff, "params") else eff.get("params", {}) | c |
| L696 | LEGACY REGISTRIES | -             fn = registry.get(name) | c |
| L697 | LEGACY REGISTRIES | -             if fn is None: | c |
| L698 | LEGACY REGISTRIES | -                 raise ValueError(f"Unknown {modality} effect: {name!r}. " | c |
| L699 | LEGACY REGISTRIES | -                                  f"Available: {list(registry.keys())}") | c |
| L700 | LEGACY REGISTRIES | -             sub_seed = hash((self.config.seed, modality, name, i)) & 0xFFFFFFFF | c |
| L701 | LEGACY REGISTRIES | -             sub_rng = np.random.default_rng(sub_seed) | c |
| L702 | LEGACY REGISTRIES | -             resolved.append((name, fn, p, params, sub_rng)) | c |
| L703 | LEGACY REGISTRIES | -         return resolved | c |
| L704 | LEGACY REGISTRIES | -  | c |
| L705 | LEGACY REGISTRIES | -     def _apply_list( | c |
| L706 | LEGACY REGISTRIES | -         self, d: dict, effects: list[tuple[str, Callable, float, dict, np.random.Generator]] | c |
| L707 | LEGACY REGISTRIES | -     ) -> dict: | c |
| L708 | LEGACY REGISTRIES | -         """Apply a list of effects with per-effect probability gating.""" | c |
| L709 | LEGACY REGISTRIES | -         for name, fn, p, params, sub_rng in effects: | c |
| L710 | LEGACY REGISTRIES | -             if sub_rng.uniform() < p: | c |
| L711 | LEGACY REGISTRIES | -                 d = fn(d, params, sub_rng) | c |
| L712 | LEGACY REGISTRIES | -         return d | c |
| L713 | LEGACY REGISTRIES | -  | c |
| L714 | LEGACY REGISTRIES | -     def __call__(self, dict_item: dict) -> dict: | c |
| L715 | LEGACY REGISTRIES | -         """Apply configured corruptions to one sample's dict_item. | c |
| L716 | LEGACY REGISTRIES | -  | c |
| L717 | LEGACY REGISTRIES | -         Order: radar → LiDAR → camera (by increasing data size). | c |
| L718 | LEGACY REGISTRIES | -         Modifies dict_item in-place and returns it. | c |
| L719 | LEGACY REGISTRIES | -  | c |
| L720 | LEGACY REGISTRIES | -         After all effects, injects metadata under | c |
| L721 | LEGACY REGISTRIES | -         ``dict_item['meta']['noise_injection']``. | c |
| L722 | LEGACY REGISTRIES | -         """ | c |
| L723 | LEGACY REGISTRIES | -         if self._radar_effects: | c |
| L724 | LEGACY REGISTRIES | -             dict_item = self._apply_list(dict_item, self._radar_effects) | c |
| L725 | LEGACY REGISTRIES | -         if self._lidar_effects: | c |
| L726 | LEGACY REGISTRIES | -             dict_item = self._apply_list(dict_item, self._lidar_effects) | c |
| L727 | LEGACY REGISTRIES | -         if self._camera_effects: | c |
| L728 | LEGACY REGISTRIES | -             dict_item = self._apply_list(dict_item, self._camera_effects) | c |
| L729 | LEGACY REGISTRIES | -  | c |
| L730 | LEGACY REGISTRIES | -         # Record metadata | c |
| L731 | LEGACY REGISTRIES | -         meta = self._metadata() | c |
| L732 | LEGACY REGISTRIES | -         if "meta" not in dict_item: | c |
| L733 | LEGACY REGISTRIES | -             dict_item["meta"] = {} | c |
| L734 | LEGACY REGISTRIES | -         dict_item["meta"]["noise_injection"] = meta | c |
| L735 | LEGACY REGISTRIES | -         return dict_item | c |
| L736 | LEGACY REGISTRIES | -  | c |
| L737 | LEGACY REGISTRIES | -     def _metadata(self) -> dict: | c |
| L738 | LEGACY REGISTRIES | -         """Return a summary of the current config for logging / audit.""" | c |
| L739 | LEGACY REGISTRIES | -         return { | c |
| L740 | LEGACY REGISTRIES | -             "seed": self.config.seed, | c |
| L741 | LEGACY REGISTRIES | -             "radar": [{"name": n, "p": p, "params": pr} for n, _, p, pr, _ in self._radar_effects], | c |
| L742 | LEGACY REGISTRIES | -             "lidar": [{"name": n, "p": p, "params": pr} for n, _, p, pr, _ in self._lidar_effects], | c |
| L743 | LEGACY REGISTRIES | -             "camera": [{"name": n, "p": p, "params": pr} for n, _, p, pr, _ in self._camera_effects], | c |
| L744 | LEGACY REGISTRIES | -         } | c |
| L969 | LEGACY REGISTRIES | + ALL_EFFECTS_LEGACY: dict[str, dict[str, Callable]] = { | c |
| L970 | LEGACY REGISTRIES | +     "radar":  RADAR_EFFECTS_LEGACY, | c |
| L971 | LEGACY REGISTRIES | +     "lidar":  LIDAR_EFFECTS_LEGACY, | c |
| L972 | LEGACY REGISTRIES | +     "camera": CAMERA_EFFECTS_LEGACY, | c |
| L973 | LEGACY REGISTRIES | + } | c |